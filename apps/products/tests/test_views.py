from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
import shutil
import os

from ..models import Category, Product
from ..views import ProductListView, ProductDetailView, ProductSearchView

User = get_user_model()

class ProductListViewTest(TestCase):
    """Test the product list view."""
    
    @classmethod
    def setUpTestData(cls):
        # Create test data
        cls.category = Category.objects.create(
            name="Coffee",
            slug="coffee",
            description="All kinds of coffee"
        )
        
        # Create test products
        cls.product1 = Product.objects.create(
            name="Arabica Coffee",
            slug="arabica-coffee",
            description="High quality Arabica coffee beans",
            price=999.99,
            category=cls.category,
            in_stock=True,
            stock_quantity=100
        )
        
        cls.product2 = Product.objects.create(
            name="Robusta Coffee",
            slug="robusta-coffee",
            description="Strong Robusta coffee beans",
            price=799.99,
            category=cls.category,
            in_stock=True,
            stock_quantity=50
        )
        
        # Create a test user
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
    
    def test_product_list_view_url_exists_at_desired_location(self):
        """Test that the product list view URL exists."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_product_list_view_uses_correct_template(self):
        """Test that the product list view uses the correct template."""
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')
    
    def test_product_list_view_lists_all_products(self):
        """Test that all products are listed on the product list page."""
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)
    
    def test_product_list_view_filters_by_category(self):
        """Test that products can be filtered by category."""
        # Create a second category
        tea_category = Category.objects.create(
            name="Tea",
            slug="tea",
            description="All kinds of tea"
        )
        
        # Create a product in the second category
        tea_product = Product.objects.create(
            name="Green Tea",
            slug="green-tea",
            description="Refreshing green tea",
            price=499.99,
            category=tea_category,
            in_stock=True,
            stock_quantity=30
        )
        
        # Test filtering by the first category
        response = self.client.get(
            reverse('products:product_list_by_category', 
                   kwargs={'category_slug': self.category.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertNotContains(response, tea_product.name)
    
    def test_product_list_view_search_functionality(self):
        """Test that the search functionality works correctly."""
        # Search for a term that matches one product
        response = self.client.get(reverse('products:product_list'), {'q': 'arabica'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertNotContains(response, self.product2.name)
        
        # Search for a term that matches no products
        response = self.client.get(reverse('products:product_list'), {'q': 'nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Товары не найдены')
    
    # Тесты сортировки были удалены


class ProductDetailViewTest(TestCase):
    """Test the product detail view."""
    
    @classmethod
    def setUpTestData(cls):
        # Create test data
        cls.category = Category.objects.create(
            name="Coffee",
            slug="coffee"
        )
        
        # Create a test product
        cls.product = Product.objects.create(
            name="Test Coffee",
            slug="test-coffee",
            description="Test description",
            price=999.99,
            category=cls.category,
            in_stock=True,
            stock_quantity=100
        )
        
        # Create a test user
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
    
    def test_product_detail_view_url_exists_at_desired_location(self):
        """Test that the product detail view URL exists."""
        url = reverse('products:product_detail', 
                     kwargs={'pk': self.product.pk, 'slug': self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_product_detail_view_uses_correct_template(self):
        """Test that the product detail view uses the correct template."""
        url = reverse('products:product_detail', 
                     kwargs={'pk': self.product.pk, 'slug': self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
    
    def test_product_detail_view_displays_correct_product(self):
        """Test that the correct product is displayed on the product detail page."""
        url = reverse('products:product_detail', 
                     kwargs={'pk': self.product.pk, 'slug': self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product'], self.product)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)
    
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Calculate expected average rating (5 + 4) / 2 = 4.5
        expected_avg = 4.5
        self.assertEqual(response.context['average_rating'], expected_avg)
    
    def test_product_detail_view_404_for_invalid_product(self):
        """Test that a 404 is returned for a non-existent product."""
        url = reverse('products:product_detail', 
                     kwargs={'pk': 9999, 'slug': 'nonexistent-product'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ProductSearchViewTest(TestCase):
    """Test the product search functionality."""
    
    @classmethod
    def setUpTestData(cls):
        # Create test data
        cls.category = Category.objects.create(
            name="Coffee",
            slug="coffee"
        )
        
        # Create test products
        cls.product1 = Product.objects.create(
            name="Arabica Coffee",
            slug="arabica-coffee",
            description="High quality Arabica coffee beans",
            price=999.99,
            category=cls.category,
            in_stock=True
        )
        
        cls.product2 = Product.objects.create(
            name="Robusta Coffee",
            slug="robusta-coffee",
            description="Strong Robusta coffee beans",
            price=799.99,
            category=cls.category,
            in_stock=True
        )
    
    def test_search_view_url_exists(self):
        """Test that the search view URL exists."""
        response = self.client.get(reverse('products:search') + '?q=arabica')
        self.assertEqual(response.status_code, 200)
    
    def test_search_view_uses_correct_template(self):
        """Test that the search view uses the correct template."""
        response = self.client.get(reverse('products:search') + '?q=arabica')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/search_results.html')
    
    def test_search_functionality(self):
        """Test that the search returns the correct results."""
        # Search for a term that matches one product
        response = self.client.get(reverse('products:search'), {'q': 'arabica'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertNotContains(response, self.product2.name)
        
        # Search for a term that matches both products
        response = self.client.get(reverse('products:search'), {'q': 'coffee'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)
        
        # Search for a term that matches no products
        response = self.client.get(reverse('products:search'), {'q': 'nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Товары не найдены')
        
        # Search with an empty query should return all products
        response = self.client.get(reverse('products:search'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)
