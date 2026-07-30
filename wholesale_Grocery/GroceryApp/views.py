from django.shortcuts import render, redirect, get_object_or_404 # render and redirect one page to another page 
from .models import Admin
from .models import Category # use of a category process
from .models import Customer
from django.contrib import messages
from .models import Contact
from .models import Product
from django.contrib.auth.decorators import login_required
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
    products = Product.objects.filter(status="True")
    return render(request,"products.html",{"products":products})

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

def login_view(request):
    if request.method == "POST":
        uname = request.POST.get('username')
        pword = request.POST.get('password')

        try:
            customer = Customer.objects.get(username=uname,password=pword)
            request.session['customer_id'] = customer.id
            request.session['customer_name'] = customer.name

            return redirect('index')

        except Customer.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid username and password'})
    return render(request, 'login.html') 

# a parts of a client side register form details.
def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        shopname = request.POST.get('shopname')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        address = request.POST.get('address')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.create_user(
            username = username,
            email = email,
            password = password,
            first_name = name
        )

        Customer.objects.create(
            user=user,
            name = name,
            shopname = shopname,
            mobile = mobile,
            email = email,
            address = address,
            username = username,
            password = password,
        )
        return redirect('login')
    return render(request,'register.html')

# client side feature user are login to close the website and client are logout 
def logout_user(request):
    request.session.flush()
    return redirect('login')

def orders(request):
    return render(request, 'orders.html')

# a part of a client side show to client order
def myorder(request):
    return render(request,'myorder.html')

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
    today = timezone.now().date()
    today_orders_count = Order.objects.filter(created_at__date=today).count()
    today_delivered_count = Order.objects.filter(created_at__date=today, order_status='Delivered').count()
    total_users_count = Customer.objects.count()
    total_delivered_count = Order.objects.filter(order_status='Delivered').count()

    context = {
        'today_orders': today_orders_count,
        'today_delivered': today_delivered_count,
        'total_users': total_users_count,
        'total_delivered': total_delivered_count,
    }
    return render(request,'admin/admin_dashboard.html')

# category parts addcategory show category.
def categories(request):
    category = Category.objects.all() # object.all() use of a all data show
    print(category)
    return render(request,'admin/category/categories.html',{"category":category})

#categoryadd parts.
# admin add category and manage category 
def category_add(request):
    if request.method == "POST":
        print(request.POST)

        Category.objects.create(
            categoryname = request.POST.get("categoryname"),
            description = request.POST.get("description"),
            status = request.POST.get("status")
        )
        return redirect('categories')
    return render(request, 'admin/category/category_add.html')

# adminside proccess admin manage product and addproduct to adminside and call to client side product page to data show.
def addproduct(request):
    if request.method == "POST":
        category =Category.objects.get(id=request.POST.get("category"))
        print(request.FILES)
        Product.objects.create(
                productname = request.POST.get('productname'),
                category = category,
                description = request.POST.get('description'),
                price=request.POST.get("price"),
                stock=request.POST.get("stock"),
                image=request.FILES.get("image"),
                status=request.POST.get("status") == "True"
        )
        return redirect("products")
    category = Category.objects.all()
    return render(request,'admin/addproduct.html',{"category":category})

# a client-side  register data
def register(request):
    if request.method == "POST":
        Customer.objects.create(
            name = request.POST.get('name'),
            shopname = request.POST.get('shopname'),
            mobile = request.POST.get('mobile'),
            email = request.POST.get('email'),
            address = request.POST.get('address'),
            username = request.POST.get('username'),
            password = request.POST.get('password')
        )
        messages.success(request,"Register Successfully Completed")
        return redirect('login')
    return render(request,'register.html')

# clien-side login proccess data
def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        customer = Customer.objects.filter(
            username = username,
            password = password
        ).first()

        if customer:
            return redirect('index')
        else:
            return redirect(request,'login.html',{'error':'Invalid Username && Password'})
    return render(request,'login.html')

#   summery oder details.
def order_summery(request, id):

    if 'customer_id' not in request.session:
        return redirect('login')

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity"))
        customername = request.POST.get("customername")
        customerphone = request.POST.get("customerphone")
        customeraddress = request.POST.get("customeraddress")

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
    product = Product.objects.all() # objects.all() a use of all data show
    return render(request,'admin/show_product.html',{"product":product})

def edit(request):
    return render(request,'admin/edit.html')

# admin logout
def admin_logout(request):
    logout(request) # admin logout ho jayega
    return redirect("admin_login")

# admin delete product manage
def delete_product(request, id):
    products = Product.objects.get(id=id)
    products.delete()
    return redirect('show_product')

# show order feature
def show_order(request):
    # objects.all() se all data show hota hai
    orders = Order.objects.all().order_by('id') # order_by('id') use a start to order number 1 

    paginator = Paginator(orders, 5) # paginator work to multiple data and manage to 1 to 5 page 

    page_number = request.GET.get('page')

    orders = paginator.get_page(page_number)
    return render(request,"admin/admin_order_show.html",{"orders":orders})

# admin delete product order manage.
def delete_order(request, pk):
    # function me primary key match hoti hai to order store hota hai
    # function nahi milta to 404 not found page call hoga 
    order = get_object_or_404(Order, id=pk)  
    order.delete()
    return redirect('admin_order_show')

def customer(request):
    customers = Customer.objects.all()
    return render(request,"admin/customer.html",{'customers':customers})

# manage payment method
def manage_payments(request):
    payments = Payment.objects.all().order_by('-created_at')
    return render(request,'admin/manage_payments.html',{'payments':payments})

# payment update feature
def update_payment(request, payment_id):

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

def manage_staff(request):
    if request.method == "POST":
        name = request.POST.get('name')
        role = request.POST.get('role')
        phone = request.POST.get('phone')

        Staff.objects.create(name=name,role=role,phone=phone) 
        return redirect('manage_staff')

    staff_list = Staff.objects.all().order_by('-id')
    return render(request,'admin/manage_staff.html',{'staff_list':staff_list})

def client_staff_view(request):
    active_staff = Staff.objects.filter(is_active=True)
    return render(request,'client_show_staff.html',{'staff_list':active_staff})

