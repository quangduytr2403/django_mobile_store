from django import template

from mobilestore.models import Product

register = template.Library()


@register.filter
def calculate_order_amount(order):
    order_amount = 0
    for product_order in order['product_order']:
        try:
            product = Product.objects.get(id=product_order['product_id'])
            order_amount += product.price * product_order['amount']
        except Product.DoesNotExist:
            pass
    return round(order_amount, 2)
