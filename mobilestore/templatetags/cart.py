from django import template
from django.forms import model_to_dict

from mobilestore.models import Product

register = template.Library()


@register.filter
def calculate_cart_amount(cart):
    cart_amount = 0
    for cart_product in cart['cart_products']:
        try:
            product = Product.objects.get(id=cart_product['product_id'])
            cart_amount += product.price * cart_product['quantity']
        except Product.DoesNotExist:
            pass
    return round(cart_amount, 2)


@register.filter
def get_cart_detail(cart):
    cart_detail = []
    for cart_product in cart['cart_products']:
        try:
            product = Product.objects.get(id=cart_product['product_id'])
            cart_detail.append({"product": model_to_dict(product), "quantity": cart_product['quantity']})
        except Product.DoesNotExist:
            pass
    return cart_detail


@register.filter
def get_number_of_products_in_cart(cart):
    return sum(item['quantity'] for item in cart['cart_products'])


@register.filter
def get_product_amount(cart_product):
    return round(cart_product['product']['price'] * cart_product['quantity'], 2)
