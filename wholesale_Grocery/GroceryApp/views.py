from django.shortcuts import render, redirect, get_object_or_404 # render and redirect one page to another page 
from .models import Admin
from .models import Category # use of a category process
from .models import Customer
from django.contrib import messages
from .models import Contact
from .models import Product, ProductImage
from django.db.models import Q
from datetime import timedelta
from .models import Order
import random
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.conf import settings
import razorpay # payment use method 
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Product
from django.core.paginator import Paginator
from django.utils import timezone
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.timezone import now
from .models import Payment
from .models import Staff
# from .form import OrderForm

client = razorpay.Client(
    auth = (
        settings.RAZORPAY_KEY_ID, #Api Key 
        settings.RAZORPAY_KEY_SECRET #Api Secret Key
    )
)
# Create your views here.
def index(request): # request() browser to request. 
    return render(request,'index.html') # render is a show html file.

# client side products to are show and client to order and purches.
def products(request):
    query = request.GET.get('query', '').strip()
    category = request.GET.get('category', '').strip()
    
    # Active products fetch કરો
    products_list = Product.objects.filter(status=True)

    # Search Query Filter
    if query:
        products_list = products_list.filter(
            Q(productname__icontains=query) | Q(description__icontains=query)
        )

    # Category Filter (અહીં category__categoryname વાપરવું)
    if category:
        if category.isdigit():
            products_list = products_list.filter(category__id=category)
        else:
            products_list = products_list.filter(category__categoryname__icontains=category)

    # Currency Conversion & Customer Logic
    c_id = request.session.get('customer_id')
    symbol = '₹'
    rate = 1.0

    if c_id:
        try:
            cust = Customer.objects.get(id=c_id)
            mobile = str(cust.mobile).strip() if cust.mobile else ''
            c_code = cust.country_code

            if not c_code or c_code == 'None':
                if mobile.startswith('+44') or mobile.startswith('44'):
                    c_code = 'GB'
                elif mobile.startswith('+1') or mobile.startswith('1'):
                    c_code = 'US'
                elif mobile.startswith('+971') or mobile.startswith('971'):
                    c_code = 'AE'
                else:
                    c_code = 'IN'

            if c_code == 'GB':
                symbol = '£'
                rate = 0.0095
            elif c_code == 'US':
                symbol = '$'
                rate = 0.012
            elif c_code == 'AE':
                symbol = 'AED '
                rate = 0.044

        except Customer.DoesNotExist:
            pass

    for p in products_list:
        try:
            p.converted_price = round(float(p.price) * float(rate), 2)
        except (ValueError, TypeError):
            p.converted_price = p.price

    return render(request, "products.html", {
        "products": products_list,
        "currency_symbol": symbol,
        "query": query,
        "selected_category": category
    })

# client side contact form are user to query are connect to admin
def contact(request):
     if request.method == "POST":
            name = request.POST.get('name')
            mobile = request.POST.get('mobile')
            email = request.POST.get('email')
            message = request.POST.get('message')

            Contact.objects.create(
                name = name,
                mobile = mobile,
                email = email,
                message = message,
            )
     return render(request,'contact.html')

CURRENCY_MAP = {
    'IN':{'symbol': '₹', 'code':'INR','rate':1.0},
    'US':{'symbol': '$', 'code':'USD', 'rate':0.012},
    'GB':{'symbol':'£', 'code':'GBP','rate':0.0095},
    'AE':{'symbol':'AED','code':'AED','rate':0.044},
}

def login_view(request):
    if request.method == "POST":
        uname = request.POST.get('username')
        pword = request.POST.get('password')

        try:
            customer = Customer.objects.get(username=uname, password=pword)

            request.session['customer_id'] = customer.id
            request.session['customer_name'] = customer.name

            # request.session['country_code'] = customer.country_code.strip().upper() if customer.country_code else 'IN'

            # return redirect('products')
            return redirect('index')

        except Customer.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid username and password'})
            
    return render(request, 'login.html')

# a parts of a client side register form details.
def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        shopname = request.POST.get('shopname')
        mobile = request.POST.get('mobile', '').strip()
        email = request.POST.get('email')
        address = request.POST.get('address')
        username = request.POST.get('username')
        password = request.POST.get('password')

        c_code = 'IN'
        c_symbol = '₹'
        c_currency = 'INR'
        c_name = 'India'

        if mobile.startswith('+44') or mobile.startswith('44'):
            c_code = 'GB'
            c_symbol = '£'
            c_currency = 'GBP'
            c_name = 'United Kingdom'
        elif mobile.startswith('+1') or mobile.startswith('1'):
            c_code = 'US'
            c_symbol = '$'
            c_currency = 'USD'
            c_name = 'United States'
        elif mobile.startswith('+971') or mobile.startswith('971'):
            c_code = 'AE'
            c_symbol = 'AED '
            c_currency = 'AED'
            c_name = 'UAE'

        otp = str(random.randint(100000, 999999))

        request.session['otp_purpose'] = 'register'
        request.session['email_otp'] = otp
        request.session['reg_data'] = {
            'name': name,
            'shopname': shopname,
            'mobile': mobile,
            'email': email,
            'address': address,
            'username': username,
            'password': password,
            'c_code': c_code,
            'c_symbol': c_symbol,
            'c_currency': c_currency,
            'c_name': c_name,
        }

        # email to send OTP
        send_mail(
            'Registration OTP - FreshMart',
            f'Your One Time Password(OTP) for FreshMart Registration is : {otp}\n\nPlease do not share this code with anyone.\n\nThank You',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return redirect('verify_otp')
    return render(request, 'register.html')

def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get('otp')
        session_otp = request.session.get('email_otp')
        purpose = request.session.get('otp_purpose')

        if user_otp and user_otp == session_otp:
            
            if purpose == 'register':
                reg_data = request.session.get('reg_data')

                if reg_data:
                    user = User.objects.create_user(
                        username=reg_data['username'],
                        email=reg_data['email'],
                        password=reg_data['password'],
                        first_name=reg_data['name']
                    )

                    Customer.objects.create(
                        user=user,
                        name=reg_data['name'],
                        shopname=reg_data['shopname'],
                        mobile=reg_data['mobile'],
                        email=reg_data['email'],
                        address=reg_data['address'],
                        username=reg_data['username'],
                        password=reg_data['password'],
                        country=reg_data['c_name'],
                        country_code=reg_data['c_code'],
                        currency_symbol=reg_data['c_symbol'],
                        currency_code=reg_data['c_currency']
                    )

                    del request.session['email_otp']
                    del request.session['otp_purpose']
                    del request.session['reg_data']

                    messages.success(request, 'Register SuccessFully')
                    return redirect('login')
                
            elif purpose == 'login':
                customer_id = request.session.get('temp_customer_id')

                try:
                    customer = Customer.objects.get(id=customer_id)
                    request.session['customer_id'] = customer.id
                    request.session['customer_name'] = customer.name
                    request.session['country_code'] = customer.country_code.strip().upper() if customer.country_code else 'IN'
                    
                    del request.session['email_otp']
                    del request.session['otp_purpose']
                    del request.session['temp_customer_id']

                    return redirect('products')
                except Customer.DoesNotExist:
                    return render(request, 'verify_otp.html', {'error': 'User not found'})

            elif purpose == 'reset_password':
                request.session.pop('email_otp', None)
                request.session.pop('otp_purpose', None)
                return redirect('reset_password')
        else:
            return render(request, 'verify_otp.html', {'error': 'Wrong OTP, Please try again!'})

    return render(request, 'verify_otp.html')   

# email to otp send
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        
        if Customer.objects.filter(email__iexact=email).exists():
            otp = str(random.randint(100000, 999999))
            request.session['reset_email'] = email
            request.session['email_otp'] = otp
            request.session['otp_purpose'] = 'reset_password'
            
            send_mail('Reset Password OTP', f'Your OTP is: {otp}', settings.EMAIL_HOST_USER, [email])
            return redirect('verify_otp')
            
        return render(request, 'forgot_password.html', {'error': 'Email Not Found'})
    
    return render(request, 'forgot_password.html')

# new password change 
def reset_password(request):
    if request.method == "POST":
        pwd = request.POST.get('password')
        confirm_pwd = request.POST.get('confirm_password')
        
        if pwd == confirm_pwd:
            email = request.session.get('reset_email')
            
            if email:
                Customer.objects.filter(email=email).update(password=pwd)
                user = User.objects.filter(email=email).first()
                if user:
                    user.set_password(pwd)
                    user.save()

                request.session.pop('reset_email', None)
                messages.success(request, 'Password updated successfully!')
                return redirect('login')
            else:
                return redirect('forgot_password')
        return render(request, 'reset_password.html', {'error': 'Passwords do not match!'})
    return render(request, 'reset_password.html')

# client side feature user are login to close the website and client are logout 
def logout_user(request):
    # only for user logout 
    if 'customer_id' in request.session:
        del request.session['customer_id']
    if 'customer_name' in request.session:
        del request.session['customer_name']
    return redirect('login')

def orders(request):
    return render(request, 'orders.html')

# a part of a client side show to client order
def myorder(request):
    return render(request,'myorder.html')

# card view
# def cart_view(request):
#     cart = request.session.get("cart", {})
#     cart_items = []
#     total_price = 0

#     for product_id, quantity in cart.items():
#         product = Product.objects.filter(id=product_id).first()
#         if product:
#             item_total = product.price * quantity
#             total_price += item_total
#             cart_items.append(
#                 {
#                     "product": product,
#                     "quantity": quantity,
#                     "item_total": item_total,
#                 }
#             )
#     context = {"cart_items": cart_items, "total_price": total_price}
#     return render(request, "cart.html", context)

# #add product to card
# def add_to_cart(request, product_id):
#     cart = request.session.get("cart", {})

#     p_id_str = str(product_id)
#     cart[p_id_str] = cart.get(p_id_str, 0) + 1

#     request.session["cart"] = cart
#     return redirect("cart_view")

# # remove item to cart
# def remove_cart(request, product_id):
#     cart = request.session.get("cart", {})
#     p_id_str = str(product_id)

#     if p_id_str in cart:
#         del cart[p_id_str]
#         request.session["cart"] = cart

#     return redirect("cart_view")

# # checkout
# def checkout_view(request):
#     cart = request.session.get('cart', {})
#     if not cart:
#         return redirect('cart_view')
    
#     request.session['cart'] = {}
    
#     return render(request, 'order_success.html')

#  a admin-login part
def admin_login(request):
    if request.method == "POST":
         username = request.POST.get('username')
         password = request.POST.get('password')

         admin = Admin.objects.filter(
             username = username, # check to admin username and password 
             password = password
         ).first()

         if admin:
             request.session['admin_id'] = admin.id
             request.session['is_admin'] = True
             return redirect('admin_dashboard')
         else:
             return redirect(request,'admin/admin_login.html',{'error': 'Invalid Login'})
    return render(request,'admin/admin_login.html')

# admin create parts.
def admin_create(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        Admin.objects.create(
            username = username,
            email = email,
            password = password
        )
        return render(request,'admin_login.html')
    return render(request,'admin/admin_create.html')

# admin dashboard admin manage all features
def admin_dashboard(request):

    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    today = now().date()
    today_orders_count = Order.objects.filter(created_at__date=today).count()
    delivered_orders_count = Order.objects.filter(order_status='Delivered').count()
    app_users_count = User.objects.filter(is_staff=False).count()
    total_orders_count = Order.objects.count()

    recent_orders = Order.objects.order_by('-id')[:5]

    context = {
        'today_orders': total_orders_count,
        'delivered_orders': delivered_orders_count,
        'app_users':app_users_count,
        'total_orders':today_orders_count,
        'recent_orders':recent_orders,
    }
    return render(request,'admin/admin_dashboard.html',context)

# category parts addcategory show category.
def categories(request):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    
    category = Category.objects.all() # object.all() use of a all data show
    print(category)
    return render(request,'admin/category/categories.html',{"category":category})

#categoryadd parts.
# admin add category and manage category 
def category_add(request):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    
    if request.method == "POST":
        print(request.POST)

        Category.objects.create(
            categoryname = request.POST.get("categoryname"),
            description = request.POST.get("description"),
            status = request.POST.get("status")
        )
        return redirect('categories')
    return render(request, 'admin/category/category_add.html')

# edir category
def edit_category(request, id):
    # fetch the category object by id or return a 404 error if not found
    category = get_object_or_404(Category, id=id)

    # check if the form is submitted via POST
    if request.method == "POST":
        category.categoryname = request.POST.get('categoryname')
        category.description = request.POST.get('description')
        # Convert status input string to a boolean value
        category.status = request.POST.get('status')

        # Save updated data into the database
        category.save()
        return redirect('categories')
    return render(request,'admin/edit.html',{'category':category})

# delete category
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('categories')

# adminside proccess admin manage product and addproduct to adminside and call to client side product page to data show.
def addproduct(request):
    # Admin Authentication Check
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    
    if request.method == "POST":
        # Selected Category Fetch
        category = Category.objects.get(id=request.POST.get("category"))
        
        # 1. Product Object Create & Save
        product = Product.objects.create(
            productname=request.POST.get('productname'),
            category=category,
            description=request.POST.get('description'),
            price=request.POST.get("price"),
            stock=request.POST.get("stock"),
            main_image=request.FILES.get("image"),
            status=request.POST.get("status") == "True"
        )

        # 2. Multiple Gallery Images Loop (ProductImage Model)
        extra_imgs = request.FILES.getlist('extra_images')
        for img in extra_imgs:
            ProductImage.objects.create(
                product=product,
                image=img
            )

        # Successful save Admin Product List
        return redirect("show_product")

    # Dropdown Active Categories or all Categories Fetch 
    category = Category.objects.filter(status='Active') if Category.objects.filter(status='Active').exists() else Category.objects.all()
    
    return render(request, 'admin/addproduct.html', {"category": category})

# a client-side  register data
# def register(request):
#     if request.method == "POST":
#         Customer.objects.create(
#             name = request.POST.get('name'),
#             shopname = request.POST.get('shopname'),
#             mobile = request.POST.get('mobile'),
#             email = request.POST.get('email'),
#             address = request.POST.get('address'),
#             username = request.POST.get('username'),
#             password = request.POST.get('password')
#         )
#         messages.success(request,"Register Successfully Completed")
#         return redirect('login')
#     return render(request,'register.html')

# # clien-side login proccess data
# def login(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         customer = Customer.objects.filter(
#             username = username,
#             password = password
#         ).first()

#         if customer:
#             return redirect('index')
#         else:
#             return redirect(request,'login.html',{'error':'Invalid Username && Password'})
#     return render(request,'login.html')

#   summery oder details.
def order_summery(request, id):

    if 'customer_id' not in request.session:
        return redirect('login')

    product = get_object_or_404(Product, id=id)

    if product.stock <= 0:
        messages.error(request, f"Sorry, '{product.productname}' Is Currently Out Of Stock")
        return redirect("products")

    if request.method == "POST":
        quantity = int(request.POST.get("quantity"))

        if quantity > product.stock:
            messages.error(request,f"Only {product.stock} items available in stock You Can  Order {quantity} items.")
            return render(request,"order_summery.html",{"product":product})
        
        customername = request.POST.get("customername")
        customerphone = request.POST.get("customerphone")
        customeraddress = request.POST.get("customeraddress")

        if len(customeraddress.strip()) < 12:
            messages.error(request,"Please Enter Full Detailed address including House No, Street/Area, and City")
            return render(request,"order_summery.html",{"product":product})

        subtotal = product.price * quantity
        gst = subtotal * 10 / 100   # gst proccess.
        total = subtotal + gst # total price

        request.session["productid"] = product.id
        request.session["quantity"] = quantity
        request.session["subtotal"] = float(subtotal)
        request.session["gst"] = float(gst)
        request.session["total"] = float(total)
        request.session["customername"] = customername
        request.session["customerphone"] = customerphone
        request.session["customeraddress"] = customeraddress
        print(request.session.items())
        return redirect("payment")

    return render(request, "order_summery.html", {"product": product})

# payment method three type method razorpay, case on delivery and creadit card
def payment(request):
    if request.method == "POST": # Use of a Method Post data are hide and secure
        payment_method = request.POST.get("payment_method")
        request.session["payment_method"] = payment_method # use of a session payment method

       # use of a if conditions 
        if payment_method == "Razorpay": # Razorpay Payment Method
            return redirect("razorpay")
        
        elif payment_method == "COD": # Case On Delivery Method
            return redirect("order_success")
        
        elif payment_method == "Credit": # Use of a Client a Credit Method
            return redirect("order_success") # order success page me redirect.
    return render(request,"payment.html") 

# razorpay payment method 
def razorpay(request):
    total = request.session.get("total")

    if not total:
        return HttpResponse("Total amount not found in session")
    amount = int(float(total) * 100)

    # client to payment to order
    try:
        payment = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        return render(request, "razorpay.html", {
            "payment": payment,
            "amount": amount,
            "total" : total,
            "key": settings.RAZORPAY_KEY_ID, # API KEY ID
        })

    except Exception as e:
        return HttpResponse(f"Razorpay Error: {e}")

# a use of a order success process
@csrf_exempt # django me decorator csrf security check to disable
def order_success(request):

    customer_id = request.session.get('customer_id')
    product_id = request.session.get("productid")

    if not customer_id: # use a if condition
        print("Session lost during Razorpay redirect")
        return redirect('login')
    
    if not product_id: # use a if condition
        return redirect("index")
    product = get_object_or_404(Product, id=product_id) # get id
    customer_obj = Customer.objects.get(id=customer_id)

   # manage to all deatils 
    order = Order.objects.create(
        customer=customer_obj, 
        customername=customer_obj.name,
        customerphone=request.session.get("customerphone"),
        customeraddress=request.session.get("customeraddress"),
        product=product,
        quantity=request.session.get("quantity"),
        totalamount=request.session.get("total"),
        payment_method=request.session.get("payment_method"),
        payment_status="Paid",
        order_status="Confirmed"
    )
    print("ORDER ID =", order.id)

    quantity = request.session.get("quantity",1)
    if product.stock >= quantity:
        product.stock -= quantity
        product.save()

    Payment.objects.create(
        order_id=f"#{order.id}",
        customer_name=customer_obj.name,
        amount=request.session.get("total"),
        payment_method=request.session.get("payment_method"),
        status="Completed"
    )
    return redirect('my_order')

# client side features client show my order.
def my_order(request):
    if 'customer_id' not in request.session: # use a session
        return redirect('login') # login me redirect 

    customer_id = request.session['customer_id']
    customer_obj = Customer.objects.get(id=customer_id)

    orders = Order.objects.filter(customer=customer_obj).order_by('-id') # ('-id') to use a lates id call

    return render(request, 'myorder.html', {'orders': orders})

# client invoice view to click all deatils show for client , client name ect. and product detail.
def invoice_view(request, id):
    order = Order.objects.get(id=id)
    return render(request,"invoice_view.html",{"order":order})

# admin side to all product show    
def show_product(request):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    
    product = Product.objects.all() # objects.all() a use of all data show
    return render(request,'admin/show_product.html',{"product":product})

def edit(request):
    return render(request,'admin/edit.html')

# admin logout
def admin_logout(request):
    if 'is_admin' in request.session:
        del request.session['is_admin']
    if 'admin_id' in request.session:
        del request.session['admin_id']

    return redirect("admin_login")

# product edit karva mate
def edit_product(request,id):

    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    
    product = get_object_or_404(Product,id=id)

    if request.method == "POST":
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.stock = int(request.POST.get('stock'))
        product.description = request.POST.get('description')

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        return redirect('show_product')
    return render(request,'admin/edit_product.html',{'product':product})

# admin delete product manage
def delete_product(request, id):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    
    products = Product.objects.get(id=id)
    products.delete()
    return redirect('show_product')

# show order feature
def show_order(request):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    # objects.all() se all data show hota hai
    orders = Order.objects.all().order_by('id') # order_by('id') use a start to order number 1 

    paginator = Paginator(orders, 5) # paginator work to multiple data and manage to 1 to 5 page 

    page_number = request.GET.get('page')

    orders = paginator.get_page(page_number)
    return render(request,"admin/admin_order_show.html",{"orders":orders})

#edit order
def edit_order(request, id):
    order = get_object_or_404(Order, id=id)

    if request.method == "POST":
        order.order_status = request.POST.get('status')
        order.payment_method = request.POST.get('payment')
        order.save()

        return redirect('admin_order_show')
    return render(request, 'admin/edit_order.html', {'order': order})

# admin delete product order manage.
def delete_order(request, pk):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    # function me primary key match hoti hai to order store hota hai
    # function nahi milta to 404 not found page call hoga 
    order = get_object_or_404(Order, id=pk)  
    order.delete()
    return redirect('admin_order_show')

# admin manage customer
def customer(request):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    customers = Customer.objects.all().order_by('id')

    paginator = Paginator(customers,10)

    page_number = request.GET.get('page')
    customers =  paginator.get_page(page_number)
    return render(request,"admin/customer.html",{'customers':customers})

#admin manage customer to edit 
def edit_customer(request, id):
    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":
        customer.name = request.POST.get('name')
        customer.shopname = request.POST.get('shopname')
        customer.mobile = request.POST.get('mobile')
        customer.email = request.POST.get('email')
        customer.address = request.POST.get('address')
        customer.username = request.POST.get('username')
        customer.password = request.POST.get('password')
        customer.save()

        return redirect('customer')

    return render(request, 'admin/edit_customer.html',{'customer':customer})

# admin delete customer
def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    return redirect('customer')


# manage payment method
def manage_payments(request):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    payments = Payment.objects.all().order_by('-created_at')
    return render(request,'admin/manage_payments.html',{'payments':payments})

# payment update feature
def update_payment(request, payment_id):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')

    payment_obj = get_object_or_404(Payment, id=payment_id)

    if request.method == "POST":
        new_status = request.POST.get('status')
        payment_obj.status = new_status
        payment_obj.save()

        clean_order_id = str(payment_obj.order_id).replace('#', '').strip()

        try:
            order_obj = Order.objects.get(id=clean_order_id)

            if new_status == "Completed":
                order_obj.payment_status = "Paid"
                order_obj.order_status = "Confirmed"
            elif new_status == "Pending":
                order_obj.payment_status = "Pending"
                order_obj.order_status = "Pending"
            elif new_status == "Failed":
                order_obj.payment_status = "Failed"
                order_obj.order_status = "Cancelled"
            
            order_obj.save()

        except Order.DoesNotExist:
            pass
    return redirect('manage_payments')

# admin side manage admin to staff 
def manage_staff(request):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    
    if request.method == "POST":
        name = request.POST.get('name')
        role = request.POST.get('role')
        phone = request.POST.get('phone')

        Staff.objects.create(name=name,role=role,phone=phone) 
        return redirect('manage_staff')

    staff_list = Staff.objects.all().order_by('-id')
    return render(request,'admin/manage_staff.html',{'staff_list':staff_list})

#admin edit and manage staff
def edit_staff(request, id):
    staff = get_object_or_404(Staff, id=id)

    if request.method == "POST":
        staff.name = request.POST.get('name')
        staff.role = request.POST.get('role')
        staff.phone = request.POST.get('phone')
        status_val = request.POST.get('status')
        staff.is_active = True if status_val in ['True','Active',True] else False

        if 'image' in request.FILES:
            staff.image = request.FILES['image']
        staff.save()
        return redirect("manage_staff")
    return render(request, 'admin/edit_staff.html',{'staff':staff})

#admin delete staff
def delete_staff(request,id):
    staff = get_object_or_404(Staff, id=id)
    staff.delete()
    return redirect("manage_staff")

# status direct toggle
def toggle_staff_status(request, id):
    staff = get_object_or_404(Staff,id=id)
    staff.is_active = not staff.is_active
    staff.save()
    return redirect("manage_staff")

# client side view the staff details
def client_staff_view(request):
    active_staff = Staff.objects.all()
    return render(request,'client_show_staff.html',{'staff_list':active_staff})

#client side client to show track order
def track_order(request,order_id):
    order_obj = get_object_or_404(Order,id=order_id)

    expected_delivery = order_obj.created_at + timedelta(days=4)

    context = {
        'order' : order_obj,
        'expected_delivery' : expected_delivery,
    }
    return render(request,'track_order.html', context)

# admin tracker order
def admin_tracker(request):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')

    orders_list = Order.objects.all().order_by('-id')
    paginator = Paginator(orders_list, 6)

    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    return render(request,'admin/admin_tracker.html',{'orders':orders})

# admin update tracker
def update_tracker(request,order_id):
    if not request.session.get('is_admin'):
        return redirect('/admin-login/')
    
    order_obj = get_object_or_404(Order,id=order_id)

    if request.method == "POST":
        new_tracking_status = request.POST.get('tracking_status')

        order_obj.tracking_status = new_tracking_status

        if new_tracking_status == "Delivered":
            order_obj.order_status = "Delivered"

        order_obj.save()

    return redirect('admin_tracker')

  

