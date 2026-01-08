from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from ..models import Category, Product

User = get_user_model()

class CategoryModelTest(TestCase):
    """Test the Category model."""
    
    def test_create_category(self):
        """Test creating a category with required fields."""
        category = Category.objects.create(
            name="Coffee",
            slug="coffee",
            description="All kinds of coffee"
        )
        self.assertEqual(str(category), category.name)
        self.assertEqual(category.slug, "coffee")
        self.assertEqual(category.description, "All kinds of coffee")
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)
        self.assertTrue(category.is_active)
    
    def test_category_ordering(self):
        """Test that categories are ordered by name by default."""
        Category.objects.create(name="Tea", slug="tea")
        Category.objects.create(name="Coffee", slug="coffee")
        categories = list(Category.objects.all())
        self.assertEqual(categories[0].name, "Coffee")
        self.assertEqual(categories[1].name, "Tea")


class ProductModelTest(TestCase):
    """Test the Product model."""
    
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.category = Category.objects.create(
            name="Coffee",
            slug="coffee",
            description="All kinds of coffee"
        )
        
    def test_create_product(self):
        """Test creating a product with required fields."""
        product = Product.objects.create(
            name="Arabica Coffee",
            slug="arabica-coffee",
            description="High quality Arabica coffee beans",
            price=999.99,
            category=self.category,
            in_stock=True,
            stock_quantity=100
        )
        
        self.assertEqual(str(product), product.name)
        self.assertEqual(product.slug, "arabica-coffee")
        self.assertEqual(product.price, 999.99)
        self.assertEqual(product.category, self.category)
        self.assertTrue(product.in_stock)
        self.assertEqual(product.stock_quantity, 100)
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)
    
    def test_product_price_validation(self):
        """Test that product price cannot be negative."""
        with self.assertRaises(ValidationError):
            product = Product(
                name="Invalid Price Product",
                slug="invalid-price",
                price=-10.00,
                category=self.category
            )
            product.full_clean()
    
    def test_product_stock_quantity_validation(self):
        """Test that stock quantity cannot be negative."""
        with self.assertRaises(ValidationError):
            product = Product(
                name="Invalid Stock Product",
                slug="invalid-stock",
                price=10.00,
                category=self.category,
                stock_quantity=-5
            )
            product.full_clean()
