from django.db import models


class Product(models.Model):
    class Meta:
        db_table = 'product'

    id = models.AutoField(primary_key=True, db_column='product_id')
    name = models.CharField(max_length=255, db_column='product_name')
    description = models.TextField(db_column='product_des')
    price = models.FloatField(db_column='product_price')
    src = models.URLField(db_column='product_img_source')
    type = models.CharField(max_length=255, db_column='product_type')
    brand = models.CharField(max_length=255, db_column='product_brand')

    def __str__(self):
        return self.name


class Order(models.Model):
    class Meta:
        db_table = 'order'

    id = models.AutoField(primary_key=True, db_column='order_id')
    userMail = models.ForeignKey('Account', on_delete=models.CASCADE, db_column='user_mail')
    orderName = models.CharField(max_length=255, db_column='order_name')
    status = models.CharField(max_length=255, db_column='order_status')
    orderDate = models.DateField(db_column='order_date')
    discount = models.CharField(max_length=255, db_column='order_discount_code')
    orderAddress = models.TextField(db_column='order_address')

    def __str__(self):
        return f"Order {self.id}: {self.orderName}"


class ProductOrder(models.Model):
    class Meta:
        db_table = 'product_order'

    order = models.ForeignKey('Order', on_delete=models.CASCADE, db_column='order_id')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='product_id')
    amount = models.IntegerField(db_column='amount_product')

    def __str__(self):
        return f"Order {self.order.id}, Product {self.product.id}: {self.product.name} - {self.amount} units"


class Account(models.Model):
    class Meta:
        db_table = 'account'

    mail = models.EmailField(primary_key=True, db_column='user_mail')
    password = models.CharField(max_length=255, db_column='password')
    role = models.CharField(max_length=255, db_column='account_role')
    name = models.CharField(max_length=255, db_column='user_name')
    address = models.TextField(db_column='user_address')
    phone = models.CharField(max_length=20, db_column='user_phone')

    def __str__(self):
        return f"Account: {self.mail}"
