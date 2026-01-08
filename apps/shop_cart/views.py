from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView

from apps.products.models import Product
from .cart import Cart
from .forms import CartAddProductForm, CartUpdateProductForm


class CartDetailView(TemplateView):
    """
    Display the shopping cart.
    """
    template_name = 'cart/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        
        # Add update form for each item in the cart
        for item in cart:
            item['update_quantity_form'] = CartUpdateProductForm(initial={
                'quantity': item['quantity'],
                'override': True
            })
            
        context['cart'] = cart
        return context


@require_POST
def cart_add(request, product_id):
    """
    Add a product to the cart or update its quantity.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST, product=product)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
        messages.success(request, _('Product added to cart'))
    
    # Redirect to the previous page or cart detail
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))


@require_POST
def cart_remove(request, product_id):
    """
    Remove a product from the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, _('Product removed from cart'))
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    """
    Update the quantity of a product in the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartUpdateProductForm(request.POST, product=product)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
        messages.success(request, _('Cart updated'))
    
    return redirect('cart:cart_detail')


def cart_clear(request):
    """
    Clear the cart.
    """
    cart = Cart(request)
    cart.clear()
    messages.success(request, _('Your cart is now empty'))
    return redirect('products:product_list')
