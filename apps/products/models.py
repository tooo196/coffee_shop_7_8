from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    """Product category model."""
    name = models.CharField(max_length=100, verbose_name=_('name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('slug'))
    description = models.TextField(blank=True, verbose_name=_('description'))
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name=_('image'))
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ('name',)
    
    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    """Product model for coffee products."""
    name = models.CharField(max_length=200, verbose_name=_('name'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('slug'))
    description = models.TextField(verbose_name=_('description'))
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name=_('price')
    )
    category = models.ForeignKey(
        Category, 
        related_name='products', 
        on_delete=models.CASCADE,
        verbose_name=_('category')
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name=_('image'))
    is_available = models.BooleanField(default=True, verbose_name=_('is available'))
    stock = models.PositiveIntegerField(default=0, verbose_name=_('stock'))
    
    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    
    # Removed Review model and average_rating property
