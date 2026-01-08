# Импорт стандартных модулей Django
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Avg, Count
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required

# Импорт моделей и форм приложения
from .models import Product, Category
from apps.shop_cart.forms import CartAddProductForm


class ProductListView(ListView):
    """
    Класс-представление для отображения списка всех товаров.
    Поддерживает пагинацию, фильтрацию по категориям, поиск и сортировку.
    """
    model = Product
    template_name = 'products/product_list.html'  # Шаблон для отображения
    context_object_name = 'products'  # Имя переменной контекста
    paginate_by = 12  # Количество товаров на странице
    
    def get_queryset(self):
        """
        Получает и фильтрует список товаров в зависимости от параметров запроса.
        
        Returns:
            QuerySet: Отфильтрованный и отсортированный список товаров
        """
        # Получаем только доступные товары с предзагрузкой категорий
        queryset = Product.objects.filter(is_available=True).select_related('category')
        
        # Фильтрация по категории, если передан category_slug
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
            
        # Поиск по запросу, если передан параметр q
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |  # Поиск по названию
                Q(description__icontains=query) |  # Поиск по описанию
                Q(category__name__icontains=query)  # Поиск по названию категории
            )
            
        # Сортировка по умолчанию - по имени
        queryset = queryset.order_by('name')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.kwargs.get('category_slug')
        context['search_query'] = self.request.GET.get('q', '')
        context['cart_product_form'] = CartAddProductForm()
        return context


class ProductDetailView(DetailView):
    """View for displaying a single product with details."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get related products (same category, excluding current product)
        related_products = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id)[:4]
        
        # Add cart product form to context
        cart_product_form = CartAddProductForm(product=product)
        
        context.update({
            'related_products': related_products,
            'cart_product_form': cart_product_form
        })
        
        return context


class ProductSearchView(TemplateView):
    """View for handling product search."""
    template_name = 'products/search_results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        if query:
            products = Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query),
                is_available=True
            ).select_related('category').distinct()
            
            # Пагинация
            paginator = Paginator(products, 12)
            page = self.request.GET.get('page')
            
            try:
                products = paginator.page(page)
            except PageNotAnInteger:
                products = paginator.page(1)
            except EmptyPage:
                products = paginator.page(paginator.num_pages)
                
            context.update({
                'products': products,
                'query': query,
                'cart_product_form': CartAddProductForm(),
            })
        
        return context
