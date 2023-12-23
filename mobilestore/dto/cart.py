from mobilestore.dto.cart_product import CartProduct


class Cart:
    def __init__(self, *args):
        if len(args) == 1:
            self.cart_products = args[0]
            return
        self.cart_products = []

    def add_product(self, product_id):
        for cart_product in self.cart_products:
            if cart_product['product_id'] == product_id:
                cart_product['quantity'] += 1
                return
        cart_product = CartProduct(product_id).to_dict()
        self.cart_products.append(cart_product)

    def change_quantity(self, item_id, quantity):
        if int(item_id) < 0 or int(item_id) > len(self.cart_products) or int(quantity) <= 0:
            return
        cart_product = self.cart_products[int(item_id) - 1]
        cart_product['quantity'] = int(quantity)

    def remove_product(self, item_id):
        if int(item_id) < 0 or int(item_id) > len(self.cart_products):
            return
        del self.cart_products[int(item_id) - 1]

    def to_dict(self):
        return {'cart_products': [cart_product for cart_product in self.cart_products]}
