import math
import re
from datetime import datetime

from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db import connection
from django.forms import model_to_dict
from django.shortcuts import render, get_object_or_404, redirect

from .dto.cart import Cart
from .models import Product, Account, Order, ProductOrder
from .utils.constants import Constants


def get_popular_products():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TOP(5) P.product_id, P.product_name, P.product_img_source
            FROM product_order AS O JOIN product AS P ON O.product_id = P.product_id
            GROUP BY P.product_id, P.product_name, P.product_img_source
            ORDER BY SUM(O.amount_product) DESC
        """)
        results = cursor.fetchall()

    popular_products = []
    for row in results:
        product_id, product_name, product_img_source = row
        popular_products.append({
            'id': product_id,
            'name': product_name,
            'src': product_img_source
        })

    return popular_products


def get_orders_by_mail(user_mail):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT  O.order_id, O.order_name, O.order_address, O.order_status, O.order_date, O.order_discount_code, 
                P.product_id, P.product_name, PO.amount_product
            FROM ([order] AS O JOIN product_order AS PO ON O.order_id = PO.order_id)
            JOIN product AS P ON PO.product_id = P.product_id
            WHERE O.user_mail = %s
            ORDER BY O.order_id
        """, [user_mail])
        results = cursor.fetchall()

    user_order = []
    cur_order_id = -1
    order = None
    product_order = []
    for row in results:
        (order_id, order_name, order_address, order_status, order_date, order_discount_code,
         product_id, product_name, amount_product) = row
        if order_id != cur_order_id:
            if order is not None:
                order["product_order"] = product_order
                user_order.append(order)

            order = {
                'order_id': order_id,
                'order_name': order_name,
                'order_status': order_status,
                'order_date': order_date,
                'order_discount_code': order_discount_code,
                'order_address': order_address
            }
            product_order = [{
                'product_id': product_id,
                'product_name': product_name,
                'amount': amount_product
            }]

            cur_order_id = order_id
        else:
            product_order.append(
                {
                    'product_id': product_id,
                    'product_name': product_name,
                    'amount': amount_product
                }
            )

    # Save last order
    if order is not None:
        order["product_order"] = product_order
        user_order.append(order)

    return user_order


def product_list(request, page_index):
    list_of_products = Product.objects.all()
    return render_list_product(list_of_products, page_index, request, 'product_list.html')


def product_search(request, page_index):
    keyword = request.GET.get("keyword", "")
    list_of_products = Product.objects.filter(name__icontains=keyword)
    return render_list_product(list_of_products, page_index, request, 'product_search.html')


def render_list_product(list_of_products, page_index, request, template):
    list_of_popular_products = get_popular_products()
    cart = request.session.get('cart', Cart().to_dict())
    user = request.session.get('user_login', None)
    items_per_page = 6
    total_page = math.ceil(len(list_of_products) / items_per_page)
    paginator = Paginator(list_of_products, items_per_page)

    try:
        products = paginator.page(page_index)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    context = {
        'list_of_products': products,
        'total_page': total_page,
        'current_page': page_index,
        'list_of_popular_products': list_of_popular_products,
        'cart': cart,
        'user_login': user
    }
    return render(request, template, context)


def product_detail(request):
    product_id = request.GET.get("id", "")
    product = get_object_or_404(Product, id=product_id)
    list_of_popular_products = get_popular_products()
    cart = request.session.get('cart', Cart().to_dict())
    user = request.session.get('user_login', None)

    context = {
        'product': product,
        'list_of_popular_products': list_of_popular_products,
        'cart': cart,
        'user_login': user
    }
    return render(request, 'product_detail.html', context)


def about_us(request):
    user = request.session.get('user_login', None)
    context = {
        'user_login': user
    }

    return render(request, 'about_us.html', context)


def login(request):
    if request.method == 'POST':
        user_mail = request.POST.get('user_mail')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user_mail_feedback = None
        password_feedback = None

        # Validate form
        check = True
        if not user_mail:
            check = False
            user_mail_feedback = Constants.EMPTY_FEEDBACK_MESSAGE

        if not password:
            check = False
            password_feedback = Constants.EMPTY_FEEDBACK_MESSAGE

        if not check:
            context = {
                'user_mail_feedback': user_mail_feedback,
                'password_feedback': password_feedback,
                'login_fail': Constants.EMPTY_LOGIN_MESSAGE,
                'user_login': {'user_mail': user_mail, 'password': password},
                'remember': remember
            }
            return render(request, 'login.html', context)

        if Account.objects.filter(mail=user_mail, password=password).exists():
            response = redirect('/store/1')
            if remember:
                # add cookies
                response.set_cookie('user_mail_cookie', user_mail, max_age=60 * 60 * 24 * 15)
                response.set_cookie('password_cookie', password, max_age=60 * 60 * 24 * 15)
            else:
                # delete cookies
                response.delete_cookie('user_mail_cookie')
                response.delete_cookie('password_cookie')

            user = get_object_or_404(Account, mail=user_mail)
            request.session['user_login'] = model_to_dict(user)
            request.session['cart'] = Cart().to_dict()
            return response
        else:
            context = {
                'login_fail': Constants.LOGIN_FAIL_MESSAGE,
                'user_login': {'user_mail': user_mail, 'password': password},
                'remember': remember,
            }
            return render(request, 'login.html', context)

    elif request.method == 'GET':
        # Get Cookies
        user_mail = request.COOKIES.get('user_mail_cookie', '')
        password = request.COOKIES.get('password_cookie', '')
        remember = 'checked' if user_mail else None

        context = {
            'user_login': {'user_mail': user_mail, 'password': password},
            'remember': remember,
        }

        return render(request, 'login.html', context)


def logout(request):
    if 'user_login' in request.session:
        del request.session['user_login']

    if 'cart' in request.session:
        del request.session['cart']

    if 'keyword' in request.session:
        del request.session['keyword']

    return redirect('login')


def register(request):
    if request.method == 'POST':
        user_mail = request.POST.get('user_mail')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        user_mail_feedback = None
        password_feedback = None
        re_password_feedback = None
        name_feedback = None
        address_feedback = None
        phone_feedback = None

        # Validate form
        check = True

        if not user_mail:
            check = False
            user_mail_feedback = Constants.EMPTY_FEEDBACK_MESSAGE
        elif not re.match(Constants.EMAIL_REGEX, user_mail):
            check = False
            user_mail_feedback = Constants.USERMAIL_FEEDBACK_MESSAGE

        if not password:
            check = False
            password_feedback = Constants.EMPTY_FEEDBACK_MESSAGE
        elif not re.match(Constants.PASSWORD_REGEX, password):
            check = False
            password_feedback = Constants.PASSWORD_FEEDBACK_MESSAGE

        if not re_password:
            check = False
            re_password_feedback = Constants.EMPTY_FEEDBACK_MESSAGE
        elif re_password != password:
            check = False
            re_password_feedback = Constants.REPASSWORD_FEEDBACK_MESSAGE

        if not name:
            check = False
            name_feedback = Constants.EMPTY_FEEDBACK_MESSAGE

        if not address:
            check = False
            address_feedback = Constants.EMPTY_FEEDBACK_MESSAGE

        if not phone:
            check = False
            phone_feedback = Constants.EMPTY_FEEDBACK_MESSAGE
        elif not re.match(Constants.PHONE_REGEX, phone):
            check = False
            phone_feedback = Constants.PHONE_FEEDBACK_MESSAGE

        if not check:
            context = {
                'user_mail_feedback': user_mail_feedback,
                'password_feedback': password_feedback,
                're_password_feedback': re_password_feedback,
                'name_feedback': name_feedback,
                'address_feedback': address_feedback,
                'phone_feedback': phone_feedback,
                'register_fail': Constants.REGISTER_FAIL_MESSAGE,
                'user_register': {'user_mail': user_mail, 'password': password, 'name': name, 'address': address,
                                  'phone': phone},
                're_password': re_password
            }
            return render(request, 'register.html', context)

        if Account.objects.filter(mail=user_mail).exists():
            context = {
                'register_fail': Constants.REGISTER_EXIST_EMAIL,
                'user_register': {'user_mail': user_mail, 'password': password, 'name': name, 'address': address,
                                  'phone': phone},
                're_password': re_password
            }
            return render(request, 'register.html', context)
        else:
            Account.objects.create(
                mail=user_mail,
                password=password,
                role=2,
                name=name,
                address=address,
                phone=phone
            )
        return redirect('login')
    elif request.method == 'GET':
        return render(request, 'register.html')


def add_to_cart(request):
    product_id = request.GET.get("id", "")
    cart_products = request.session['cart']['cart_products']
    cart = Cart(cart_products)
    cart.add_product(product_id)
    request.session['cart'] = cart.to_dict()

    return redirect('/store/detail?id=' + product_id)


def show_cart(request):
    cart = request.session['cart']
    user = request.session['user_login']
    context = {
        'cart': cart,
        'user_login': user
    }
    return render(request, 'cart.html', context)


def change_quantity(request):
    item_id = request.GET.get("id", "")
    quantity = request.GET.get("quantity")
    cart_products = request.session['cart']['cart_products']
    cart = Cart(cart_products)
    cart.change_quantity(item_id, quantity)
    request.session['cart'] = cart.to_dict()

    return redirect('/store/cart/show-cart')


def remove_product(request):
    item_id = request.GET.get("id", "")
    cart_products = request.session['cart']['cart_products']
    cart = Cart(cart_products)
    cart.remove_product(item_id)
    request.session['cart'] = cart.to_dict()

    return redirect('/store/cart/show-cart')


def submit_order(request):
    user_login = request.session.get('user_login', None)
    user_mail = user_login.get('mail', '')
    cart = request.session.get('cart', Cart().to_dict())
    customer_name = request.GET.get('customer_name', '')
    customer_address = request.GET.get('customer_address', '')
    discount = request.GET.get('discount', '')

    customer_name_feedback = None
    customer_address_feedback = None
    discount_feedback = None

    # Validate form
    check = True
    if not customer_name:
        check = False
        customer_name_feedback = Constants.EMPTY_FEEDBACK_MESSAGE
    if not customer_address:
        check = False
        customer_address_feedback = Constants.EMPTY_FEEDBACK_MESSAGE
    if not re.match(Constants.DISCOUNT_REGEX, discount):
        check = False
        discount_feedback = Constants.DISCOUNT_FEEDBACK_MESSAGE

    if not check:
        context = {
            'user_login': user_login,
            'cart': cart,
            'customer_name_feedback': customer_name_feedback,
            'customer_address_feedback': customer_address_feedback,
            'discount_feedback': discount_feedback,
            'order': {"customer_name": customer_name, "discount": discount, "customer_address": customer_address}
        }
        return render(request, 'cart.html', context)

    created_order = Order.objects.create(
        userMail=Account.objects.get(mail=user_mail),
        orderName=customer_name,
        status="ACCEPTED",
        orderDate=datetime.now().date().isoformat(),
        discount=discount,
        orderAddress=customer_address
    )

    cart_products = cart['cart_products']
    for cart_product in cart_products:
        ProductOrder.objects.create(
            order=created_order,
            product=Product.objects.get(id=cart_product['product_id']),
            amount=cart_product['quantity']
        )

    # Reset cart
    request.session['cart'] = Cart().to_dict()
    return redirect('/store/show-history')


def show_history(request):
    user_login = request.session.get('user_login', None)
    user_mail = '' if user_login is None else user_login.get('mail', '')

    user_order = get_orders_by_mail(user_mail)

    context = {
        'user_login': user_login,
        'list_of_orders': user_order
    }

    return render(request, 'show_history.html', context)
