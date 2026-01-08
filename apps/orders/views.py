from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F, DecimalField, Count
from django.db.models.functions import Coalesce, TruncDate
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, HttpResponse, HttpResponseServerError, HttpResponseRedirect, FileResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.forms import modelform_factory
import os

from .models import Order, OrderItem
from apps.products.models import Product
from apps.shop_cart.cart import Cart
from .pdf_utils import generate_invoice_pdf, generate_receipt_pdf


@login_required
def checkout(request):
    """
    Оформление заказа аутентифицированным пользователем
    """
    cart = Cart(request)
    if not cart:
        messages.warning(request, _('Ваша корзина пуста'))
        return redirect('cart:cart_detail')
    
    # Получаем или создаем профиль пользователя
    user = request.user
    
    if request.method == 'POST':
        # Создаем заказ
        order = Order.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone if hasattr(user, 'phone') else '',
            address=user.address if hasattr(user, 'address') else '',
            postal_code=user.postal_code if hasattr(user, 'postal_code') else '',
            city=user.city if hasattr(user, 'city') else '',
            country=user.country if hasattr(user, 'country') else '',
        )
        
        # Добавляем товары в заказ
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )
        
        # Очищаем корзину
        cart.clear()
        
        # Перенаправляем на страницу успешного оформления заказа
        return redirect('orders:order_created', order_id=order.id)
    
    return render(request, 'orders/checkout.html', {'cart': cart})


def guest_checkout(request):
    """
    Оформление заказа без регистрации
    """
    cart = Cart(request)
    if not cart:
        messages.warning(request, _('Ваша корзина пуста'))
        return redirect('cart:cart_detail')
    
    # Создаем форму для гостевого заказа
    OrderForm = modelform_factory(Order, fields=('first_name', 'last_name', 'email', 'phone', 'address', 'postal_code', 'city', 'country'))
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = form.save(commit=False)
            order.save()
            
            # Добавляем товары в заказ
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Очищаем корзину
            cart.clear()
            
            # Перенаправляем на страницу успешного оформления заказа
            return redirect('orders:order_created', order_id=order.id)
    else:
        form = OrderForm()
    
    return render(request, 'orders/guest_checkout.html', {'cart': cart, 'form': form})


def order_created(request, order_id):
    """
    Страница успешного оформления заказа
    """
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_created.html', {'order': order})


class OrderListView(LoginRequiredMixin, ListView):
    """Список заказов пользователя"""
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    """Детали заказа"""
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@login_required
def order_create(request):
    """Создание заказа из корзины"""
    cart = Cart(request)
    
    if not cart:
        messages.warning(request, _('Ваша корзина пуста'))
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            comment=request.POST.get('comment', ''),
            delivery_type=request.POST.get('delivery_type', 'self'),
            payment_method=request.POST.get('payment_method', 'online'),
            status=Order.Status.PENDING
        )
        
        # Добавляем товары из корзины в заказ
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )
        
        # Очищаем корзину
        cart.clear()
               
        messages.success(request, _('Ваш заказ успешно оформлен! Номер вашего заказа: ') + str(order.id))
        return redirect('orders:order_detail', order_id=order.id)
    
    return render(request, 'orders/order_create.html', {'cart': cart})


@login_required
def order_cancel(request, order_id):
    """Отмена заказа пользователем"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status in [Order.Status.PENDING, Order.Status.PROCESSING]:
        order.status = Order.Status.CANCELLED
        order.save()
        messages.success(request, _('Заказ успешно отменен'))
    else:
        messages.error(request, _('Невозможно отменить заказ в текущем статусе'))
    
    return redirect('orders:order_detail', order_id=order.id)


@login_required
def order_track(request, order_id):
    """Отслеживание заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_track.html', {'order': order})


# AJAX представления
@login_required
@require_POST
def update_order_status(request, order_id):
    """Обновление статуса заказа (AJAX)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)
    
    if request.method == 'POST' and request.is_ajax():
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.Status.choices):
            order.status = new_status
            order.save()
            return JsonResponse({'status': 'success', 'new_status': order.get_status_display()})
        
        return JsonResponse({'error': 'Неверный статус'}, status=400)
    
    return JsonResponse({'error': 'Неверный запрос'}, status=400)


# Представления для обработки платежей
@require_http_methods(["POST"])
@login_required
def payment_process(request):
    """Обработка платежа"""
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    # Здесь должна быть логика обработки платежа через платежный шлюз
    # В данном примере просто помечаем заказ как оплаченный
    order.paid = True
    order.save()
    
    return JsonResponse({'status': 'success', 'order_id': order.id})


@login_required
def payment_completed(request):
    """Успешная оплата"""
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    if not order.paid:
        order.paid = True
        order.save()
    
    return render(request, 'orders/payment/completed.html', {'order': order})


@login_required
def payment_canceled(request):
    """Отмена оплаты"""
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/payment/canceled.html', {'order': order})


# Административные отчеты
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_order_report(request):
    """Отчет по заказам для администратора"""
    orders = Order.objects.all().order_by('-created_at')
    
    # Фильтрация по дате, если указана
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        orders = orders.filter(created_at__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__lte=date_to)
    
    # Пагинация
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/reports/orders.html', {
        'page_obj': page_obj,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_sales_report(request):
    """Отчет по продажам для администратора"""
    # Получаем данные о продажах по категориям
    sales_by_category = OrderItem.objects.values(
        'product__category__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('price') * F('quantity'), output_field=DecimalField())
    ).order_by('-total_revenue')
    
    # Получаем данные о продажах по дням
    sales_by_day = Order.objects.filter(paid=True).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total_orders=Count('id'),
        total_revenue=Sum('get_total_cost')
    ).order_by('date')
    
    # Фильтрация по дате, если указана
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        sales_by_category = sales_by_category.filter(order__created_at__gte=date_from)
        sales_by_day = sales_by_day.filter(date__gte=date_from)
    if date_to:
        sales_by_category = sales_by_category.filter(order__created_at__lte=date_to)
        sales_by_day = sales_by_day.filter(date__lte=date_to)
    
    return render(request, 'admin/reports/sales.html', {
        'sales_by_category': sales_by_category,
        'sales_by_day': sales_by_day,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def order_invoice_pdf(request, order_id):
    """Генерация PDF счета на оплату"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    try:
        # Генерируем PDF
        pdf = generate_invoice_pdf(order)
        
        # Создаем ответ с PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
        response.write(pdf)
        return response
        
    except Exception as e:
        # В случае ошибки возвращаем сообщение об ошибке
        messages.error(request, _('Произошла ошибка при генерации счета. Пожалуйста, попробуйте позже.'))
        return redirect('orders:order_detail', order_id=order.id)


@login_required
def order_receipt_pdf(request, order_id):
    """Генерация PDF чека"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    try:
        # Генерируем PDF
        pdf = generate_receipt_pdf(order)
        
        # Создаем ответ с PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{order.id}.pdf"'
        response.write(pdf)
        return response
        
    except Exception as e:
        # В случае ошибки возвращаем сообщение об ошибке
        messages.error(request, _('Произошла ошибка при генерации чека. Пожалуйста, попробуйте позже.'))
        return redirect('orders:order_detail', order_id=order.id)


# Вспомогательные функции
def get_order_summary(user):
    """Получение сводной информации о заказах пользователя"""
    orders = Order.objects.filter(user=user)
    
    total_orders = orders.count()
    total_spent = orders.aggregate(
        total=Coalesce(Sum('total_amount'), 0, output_field=DecimalField())
    )['total']
    
    return {
        'total_orders': total_orders,
        'total_spent': total_spent,
        'last_orders': orders.order_by('-created_at')[:5]
    }
