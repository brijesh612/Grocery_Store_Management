from django.urls import path
from . import views

# urls parts all urls.
# path('products/')-> Browser Link To A Urls
urlpatterns = [
    path('', views.index, name='index'),
    path('products/',views.products, name='products'),
    path('contact/',views.contact, name='contact'),
    path('login/',views.login_view, name='login'),
    path('register/',views.register, name='register'),
    path('logout/',views.logout_user,name='logout'),
    path('orders/', views.orders,name='orders'),
    path('my-order/',views.my_order,name='my_order'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-create/', views.admin_create, name='admin_create'), # admin-create use to create a admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('categories/', views.categories, name='categories'),
    path('category-add/',views.category_add,name='category_add'),
    path('addproduct',views.addproduct,name='addproduct'),
    path("order-summery/<int:id>",views.order_summery, name="order_summery"),
    path("payment/",views.payment,name="payment"),
    path("razorpay/",views.razorpay,name="razorpay"),
    path("order-success/",views.order_success,name="order_success"),
    path("invoice-view/<int:id>/",views.invoice_view,name="invoice_view"),
    path("show-product/",views.show_product,name="show_product"),
    path("edit/",views.edit,name="edit"),
    path("admin-logout/",views.admin_logout,name="admin_logout"),
    path("delete/<int:id>/",views.delete_product,name="delete_product"),
    path("admin-orders/",views.show_order,name="admin_order_show"),
    path("delete-order/<int:pk>/",views.delete_order, name='delete_order'),
    path("customer-list/",views.customer,name="customer"),
    path("admin-panel/payments",views.manage_payments,name="manage_payments"),
    path("admin-panel/payments/update/<int:payment_id>/",views.update_payment,name="update_payment"),
    path("admin-panel/staff/",views.manage_staff,name="manage_staff"),
    path("client_show_staff",views.client_staff_view,name="client_show_staff"),
    # path('register/',views.register,name='register'),
    # path('login/',views.login,name='login'),

]