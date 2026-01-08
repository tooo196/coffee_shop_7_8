from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    # Оформление заказа
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/guest/', views.guest_checkout, name='guest_checkout'),
    
    # Заказы
    path('create/', views.order_create, name='order_create'),
    path('created/<int:order_id>/', views.order_created, name='order_created'),
    path('history/', views.OrderListView.as_view(), name='order_history'),
    path('detail/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('cancel/<int:order_id>/', views.order_cancel, name='order_cancel'),
    path('track/<int:order_id>/', views.order_track, name='order_track'),
    
    # Оплата
    path('payment/process/', views.payment_process, name='payment_process'),
    path('payment/completed/', views.payment_completed, name='payment_completed'),
    path('payment/canceled/', views.payment_canceled, name='payment_canceled'),
    
    # Отчеты для администратора
    path('admin/reports/orders/', views.admin_order_report, name='admin_order_report'),
    path('admin/reports/sales/', views.admin_sales_report, name='admin_sales_report'),
]
