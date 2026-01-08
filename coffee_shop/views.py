from django.shortcuts import render

# Представление для страницы "О нас"
def about(request):
    """
    Отображает страницу 'О нас'.
    
    Args:
        request: Объект HTTP-запроса
        
    Returns:
        HTTP-ответ с отрендеренным шаблоном about.html
    """
    return render(request, 'about.html')

# Представление для страницы контактов
def contact(request):
    """
    Отображает страницу контактов.
    
    Args:
        request: Объект HTTP-запроса
        
    Returns:
        HTTP-ответ с отрендеренным шаблоном contact.html
    """
    return render(request, 'contact.html')