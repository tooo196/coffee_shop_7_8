"""
Конфигурация URL для проекта coffee_shop.

Список `urlpatterns` связывает URL с представлениями. Подробнее:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/

Примеры:
Функции-представления:
    1. Импортируйте представление: from my_app import views
    2. Добавьте URL в urlpatterns: path('', views.home, name='home')

Класс-представления:
    1. Импортируйте класс представления: from other_app.views import Home
    2. Добавьте URL в urlpatterns: path('', Home.as_view(), name='home')

Включение других URLconf:
    1. Импортируйте функцию include: from django.urls import include, path
    2. Добавьте URL в urlpatterns: path('blog/', include('blog.urls'))
"""
# Импорт стандартных модулей Django
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Импорт представлений текущего приложения
from . import views

# Основные URL-маршруты приложения
urlpatterns = [
    # Админ-панель Django
    path('admin/', admin.site.urls),
    
    # Главная страница (каталог товаров)
    path('', include('apps.products.urls', namespace='products')),
    
    # Аутентификация и профиль пользователя
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    
    # Оформление и управление заказами
    path('orders/', include('apps.orders.urls', namespace='orders')),
    
    # Корзина покупок
    path('cart/', include('apps.shop_cart.urls', namespace='cart')),
    
    # Статические страницы
    path('about/', views.about, name='about'),  # Страница "О нас"
    path('contact/', views.contact, name='contact'),  # Страница контактов
]

# Обслуживание медиафайлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# Добавление Django Debug Toolbar в режиме разработки
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        # URL для отладки
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
