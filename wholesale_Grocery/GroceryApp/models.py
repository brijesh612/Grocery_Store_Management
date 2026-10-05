from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

# models are a database create a table.
class Category(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )
    categoryname = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.categoryname
     
# admin side new admin create 
class Admin(models.Model):
    username = models.CharField(max_length=70, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

#clientside customer details table
class Customer(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)
    shopname = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    country = models.CharField(max_length=50,null=True,blank=True)
    country_code = models.CharField(max_length=10,null=True, blank=True)
    currency_symbol = models.CharField(max_length=10,null=True, blank=True)
    currency_code = models.CharField(max_length=10,null=True, blank=True)
    email = models.EmailField(unique=True)
    address = models.TextField()
    username = models.CharField(max_length=100,unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# product table mange a product
class Product(models.Model):
    productname = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveBigIntegerField(default=0)
    main_image = models.ImageField(upload_to='products/', null=True, blank=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.productname

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/', null=True, blank=True)

    def __str__(self):
        return f"{self.product.productname} Image"
    
# order table
class Order(models.Model):

    customer = models.ForeignKey(Customer,on_delete=models.CASCADE, null=True,blank=True)
    customername =  models.CharField(max_length=150)
    customerphone = models.CharField(max_length=15)
    customeraddress = models.TextField()

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    totalamount = models.DecimalField(max_digits=10,decimal_places=2)
    payment_method = models.CharField(max_length=50)

    payment_status = models.CharField(
        max_length=20,
        default="Pending"
    )
    order_status = models.CharField(
        max_length=20,
        default="Pending"
    )
    TRACKING_CHOICES =[
        ('Order Placed','Order Placed'),
        ('Shipped','Shipped'),
        ('Out For Delivery','Out For Delivery'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled'),
    ]
    tracking_status = models.CharField(max_length=60,choices=TRACKING_CHOICES,default='Order Placed')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    shipped_at = models.DateTimeField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True,blank=True)
    deliverd_at = models.DateTimeField(null=True,blank=True)

    def save(self, *args, **kwargs):
        status_fields = {
            'Shipped': 'shipped_at',
            'Out For Delivery': 'out_for_delivery_at',
            'Delivered': 'delivered_at',
        }

        field_name = status_fields.get(self.tracking_status)
        if field_name and not getattr(self, field_name):
            setattr(self, field_name, timezone.now())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id}-{self.customername}"
    
# client side contact table details
class Contact(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    message = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# payment table admin manage a payment pending, complete and failed
class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending','Pending'),
        ('Completed','Completed'),
        ('Failed','Failed'),
    ]

    order_id = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    payment_method = models.CharField(max_length=50,default='UPI')
    status = models.CharField(max_length=20,choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.customer_name}"

class Staff(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True,null=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='staff/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.role})"
