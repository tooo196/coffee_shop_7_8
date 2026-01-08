from django.urls import path
from django.views.generic import ListView, DetailView

from . import views
from .models import Product, Category

app_name = 'products'

urlpatterns = [
    # Список товаров и детальная страница
    path('', views.ProductListView.as_view(), name='product_list'),
    path('category/<slug:category_slug>/', views.ProductListView.as_view(), name='product_list_by_category'),
    path('<int:pk>/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Поиск
    path('search/', views.ProductSearchView.as_view(), name='search'),
]
