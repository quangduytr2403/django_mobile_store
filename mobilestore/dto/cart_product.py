class CartProduct:
    def __init__(self, product_id):
        self.product_id = product_id
        self.quantity = 1

    def __str__(self):
        return f"{self.product_id} - {self.quantity} units"

    def to_dict(self):
        return {'product_id': self.product_id, 'quantity': self.quantity}
