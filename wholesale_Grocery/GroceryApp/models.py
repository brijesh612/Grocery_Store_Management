from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# models are a database create a table.
class Category(models.Model): # category table
    STATUS_CHOICES = (
        ('Active','Active'),
        ('Inactive','Inactive'),
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
    email = models.EmailField(unique=True)
    address = models.TextField()
    username = models.CharField(max_length=100,unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# product table mange a product
class Product(models.Model):
    productname   = models.CharField(max_length=200)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.PositiveBigIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.productname 

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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customername
    
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

    def __str__(self):
        return f"{self.name} ({self.role})"