from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _

from .models import Product, Category


class ProductSearchForm(forms.Form):
    """Form for searching products."""
    SORT_CHOICES = [
        ('name', _('Name (A-Z)')),
        ('-name', _('Name (Z-A)')),
        ('price', _('Price (low to high)')),
        ('-price', _('Price (high to low)')),
        ('-created_at', _('Newest first')),
        ('-popularity', _('Most popular')),
    ]

    q = forms.CharField(
        label=_('Search'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search products...'),
            'aria-label': _('Search products')
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label=_('Category'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        label=_('Min Price'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Min'),
            'step': '0.01',
            'min': '0'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        label=_('Max Price'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Max'),
            'step': '0.01',
            'min': '0'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        label=_('Sort By'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    in_stock = forms.BooleanField(
        required=False,
        label=_('In Stock Only'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
    
    def search(self):
        """Perform the search based on form data."""
        queryset = Product.objects.filter(is_available=True)
        data = self.cleaned_data
        
        if data.get('q'):
            queryset = queryset.filter(
                Q(name__icontains=data['q']) |
                Q(description__icontains=data['q']) |
                Q(category__name__icontains=data['q'])
            )
            
        if data.get('category'):
            queryset = queryset.filter(category=data['category'])
            
        if data.get('min_price') is not None:
            queryset = queryset.filter(price__gte=data['min_price'])
            
        if data.get('max_price') is not None:
            queryset = queryset.filter(price__lte=data['max_price'])
            
        if data.get('in_stock'):
            queryset = queryset.filter(stock__gt=0)
            
        if data.get('sort_by'):
            sort_by = data['sort_by']
            if sort_by == 'popularity':
                # Предполагаем, что у нас есть поле 'popularity' или мы можем его вычислить
                queryset = queryset.annotate(
                    num_orders=Count('order_items')
                ).order_by('-num_orders')
            else:
                queryset = queryset.order_by(sort_by)
                
        return queryset.distinct()


class CartAddProductForm(forms.Form):
    """Form for adding a product to the cart."""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control quantity-input',
            'style': 'width: 70px; display: inline-block;'
        })
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )
    
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        
        if self.product and self.product.stock < 20:
            self.fields['quantity'].max_value = self.product.stock
            
            if self.product.stock == 0:
                self.fields['quantity'].widget.attrs['disabled'] = True
                self.fields['quantity'].help_text = _('Out of stock')
