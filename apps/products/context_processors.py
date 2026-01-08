from .models import Category

def categories(request):
    """
    Context processor that makes categories available to all templates.
    """
    return {
        'categories': Category.objects.all()
    }
