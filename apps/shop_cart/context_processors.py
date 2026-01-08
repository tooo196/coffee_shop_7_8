from .cart import Cart

def cart(request):
    """
    Context processor that makes the cart available to all templates.
    """
    return {'cart': Cart(request)}
