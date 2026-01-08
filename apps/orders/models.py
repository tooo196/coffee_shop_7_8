from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel
from apps.products.models import Product
from apps.accounts.models import User, GuestSession


class Order(TimeStampedModel):
    """Order model for customer purchases."""
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        SHIPPED = 'SHIPPED', _('Shipped')
        DELIVERED = 'DELIVERED', _('Delivered')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
        verbose_name=_('user')
    )
    guest_session = models.ForeignKey(
        GuestSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('guest session')
    )
    first_name = models.CharField(max_length=50, verbose_name=_('first name'))
    last_name = models.CharField(max_length=50, verbose_name=_('last name'))
    email = models.EmailField(verbose_name=_('email'))
    address = models.TextField(verbose_name=_('address'))
    postal_code = models.CharField(max_length=20, verbose_name=_('postal code'))
    city = models.CharField(max_length=100, verbose_name=_('city'))
    phone = models.CharField(max_length=20, verbose_name=_('phone'))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('status')
    )
    paid = models.BooleanField(default=False, verbose_name=_('paid'))
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('total cost')
    )
    
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ('-created_at',)
    
    def __str__(self):
        return f"Order {self.id}"
    
    def get_total_cost(self):
        """Calculate total cost of the order."""
        return sum(item.get_cost() for item in self.items.all())
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # Новый заказ, устанавливаем общую стоимость
            self.total_cost = self.get_total_cost()
        super().save(*args, **kwargs)


class OrderItem(TimeStampedModel):
    """Items in an order."""
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name=_('order')
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.CASCADE,
        verbose_name=_('product')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('price')
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_('quantity')
    )
    
    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def get_cost(self):
        """Calculate cost of the order item."""
        return self.price * self.quantity
