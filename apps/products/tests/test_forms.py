from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.images import ImageFile
import tempfile
import shutil
import os

from django.contrib.auth import get_user_model
from ..models import Category, Product
from ..forms import ProductForm

User = get_user_model()


class ProductFormTest(TestCase):
    """Test the ProductForm."""
    
    @classmethod
    def setUpTestData(cls):
        # Create test category
        cls.category = Category.objects.create(
            name="Coffee",
            slug="coffee"
        )
        
        # Create a test user
        cls.user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123"
        )
        
        # Create a temporary directory for test uploads
        cls.temp_media_root = tempfile.mkdtemp()
    
    @classmethod
    def tearDownClass(cls):
        # Clean up the temporary directory
        shutil.rmtree(cls.temp_media_root, ignore_errors=True)
        super().tearDownClass()
    
    def test_product_form_valid_data(self):
        """Test ProductForm with valid data."""
        form_data = {
            'name': 'Test Product',
            'slug': 'test-product',
            'description': 'Test description',
            'price': '9.99',
            'category': self.category.id,
            'in_stock': True,
            'stock_quantity': '10',
            'is_available': True
        }
        
        # Create a test image
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'simple image content',
            content_type='image/jpeg'
        )
        
        form = ProductForm(
            data=form_data,
            files={'image': image}
        )
        
        self.assertTrue(form.is_valid())
    
    def test_product_form_missing_required_fields(self):
        """Test ProductForm with missing required fields."""
        # Test missing name
        form_data = {
            'slug': 'test-product',
            'description': 'Test description',
            'price': '9.99',
            'category': self.category.id,
            'in_stock': True,
            'stock_quantity': '10',
            'is_available': True
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
        # Test missing price
        form_data = {
            'name': 'Test Product',
            'slug': 'test-product',
            'description': 'Test description',
            'category': self.category.id,
            'in_stock': True,
            'stock_quantity': '10',
            'is_available': True
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
    
    def test_product_form_price_validation(self):
        """Test ProductForm price validation."""
        # Test negative price
        form_data = {
            'name': 'Test Product',
            'slug': 'test-product',
            'description': 'Test description',
            'price': '-10.00',
            'category': self.category.id,
            'in_stock': True,
            'stock_quantity': '10',
            'is_available': True
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        
        # Test zero price (should be allowed for free products)
        form_data['price'] = '0.00'
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_product_form_stock_quantity_validation(self):
        """Test ProductForm stock quantity validation."""
        # Test negative stock quantity
        form_data = {
            'name': 'Test Product',
            'slug': 'test-product',
            'description': 'Test description',
            'price': '9.99',
            'category': self.category.id,
            'in_stock': True,
            'stock_quantity': '-5',
            'is_available': True
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('stock_quantity', form.errors)
        
        # Test zero stock quantity (should be allowed)
        form_data['stock_quantity'] = '0'
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_product_form_slug_auto_generation(self):
        """Test that slug is auto-generated from name if not provided."""
        form_data = {
            'name': 'Test Product With Long Name',
            'description': 'Test description',
            'price': '9.99',
            'category': self.category.id,
            'in_stock': True,
            'stock_quantity': '10',
            'is_available': True
        }
        
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())
        product = form.save()
        self.assertEqual(product.slug, 'test-product-with-long-name')
