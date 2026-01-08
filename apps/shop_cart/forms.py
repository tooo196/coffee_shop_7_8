from django import forms
from django.forms import ModelForm
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from apps.products.models import Product


class CartAddProductForm(forms.Form):
    """
    Form for adding products to the cart.
    """
    quantity = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control quantity-input',
            'style': 'width: 70px; display: inline-block;'
        }),
        label=_('Quantity')
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


class CartUpdateProductForm(CartAddProductForm):
    """
    Form for updating product quantity in the cart.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['override'].initial = True
