"""Tests for models"""

from unittest.mock import patch
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from django.contrib.auth import get_user_model

from core import models


def create_user(username='testuser', email='test@example.com', password='testpass123'):
    """Create and return a new user"""
    return get_user_model().objects.create_user(username=username, email=email, password=password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@EXAMPLE.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@EXAMPLE.com', 'test4@example.com'],
        ]
        for email, excepted in sample_emails:
            user = create_user(email=email, password='sample123')
            self.assertEqual(user.email, excepted)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class PostTests(TestCase):
    """Test posts"""

    def test_create_post(self):
        user = create_user()
        category = models.Category.objects.create(
            name='Category1'
        )
        post = models.Post.objects.create(
            title='Post1',
            content='Post1 content',
            user=user,
            category=category
        )
        self.assertEqual(post.title, 'Post1')
        self.assertEqual(post.content, 'Post1 content')

    @patch('core.models.uuid.uuid4')
    def test_post_file_name_uuid(self, mock_uuid):
        """Test generating image path for post image"""

        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.post_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/post/{uuid}.jpg')


class ProductTests(TestCase):
    """Test products"""

    def test_create_product(self):
        category = models.Category.objects.create(
            name='Category1'
        )
        product = models.Product.objects.create(
            name='Product1',
            description='Product1 description',
            price=Decimal('5.50'),
            stock=10,
            is_hot=True,
            is_on_sale=False,
            is_featured=False,
            is_trending=False,
            sale_amount=0,
            view_count=0,
            category=category
        )
        self.assertEqual(product.name, 'Product1')
        self.assertLessEqual(product.created_at, product.updated_at)
        self.assertEqual(product.view_count, 0)
        self.assertEqual(product.sale_amount, 0)
        self.assertEqual(product.is_featured, False)
        self.assertEqual(product.is_trending, False)

    def test_create_rating(self):
        user = create_user()
        category = models.Category.objects.create(
            name='Category1'
        )
        product = models.Product.objects.create(
            name='Product1',
            description='Product1 description',
            price=Decimal('5.50'),
            stock=10,
            is_hot=True,
            is_on_sale=False,
            category=category
        )
        rating = models.Rating.objects.create(
            rating=3,
            user=user,
            product=product
        )
        self.assertEqual(rating.rating, 3)

    @patch('core.models.uuid.uuid4')
    def test_product_image_file_name_uuid(self, mock_uuid):
        """Test generating image path for product image"""

        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.product_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/product/{uuid}.jpg')


class CategoryTests(TestCase):
    """Test categories"""

    def test_create_category(self):
        category = models.Category.objects.create(
            name='Category1'
        )
        self.assertEqual(category.name, 'Category1')

    @patch('core.models.uuid.uuid4')
    def test_category_file_name_uuid(self, mock_uuid):
        """Test generating image path for category image"""

        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.category_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/category/{uuid}.jpg')


class ReviewTests(TestCase):
    """Test reviews"""

    def test_create_review(self):
        user = create_user()
        category = models.Category.objects.create(
            name='Category1'
        )
        product = models.Product.objects.create(
            name='Product1',
            description='Product1 description',
            price=Decimal('5.50'),
            stock=10,
            is_hot=True,
            is_on_sale=False,
            category=category
        )
        review = models.Review.objects.create(
            content='Test review',
            user=user,
            product=product
        )
        self.assertEqual(review.content, 'Test review')


class ProductFeatureTests(TestCase):
    """Test product features"""

    def test_create_product_feature(self):
        category = models.Category.objects.create(
            name='Category1'
        )
        product = models.Product.objects.create(
            name='Product1',
            description='Product1 description',
            price=Decimal('5.50'),
            stock=10,
            is_hot=True,
            is_on_sale=False,
            category=category
        )
        feature = models.ProductFeature.objects.create(
            feature='Test feature',
            product=product
        )
        self.assertEqual(feature.feature, 'Test feature')


class FavoriteTests(TestCase):
    """Test favorites"""

    def test_create_favorite(self):
        user = create_user()
        category = models.Category.objects.create(
            name='Category1'
        )
        product = models.Product.objects.create(
            name='Product1',
            description='Product1 description',
            price=Decimal('5.50'),
            stock=10,
            is_hot=True,
            is_on_sale=False,
            category=category
        )
        favorite = models.Favorite.objects.create(
            user=user,
            product=product
        )
        self.assertEqual(favorite.user, user)


class CouponTests(TestCase):
    """Test coupons"""

    def test_create_coupon(self):
        coupon = models.Coupon.objects.create(
            code='TestCode',
            discount=Decimal('0.10'),
            uses_limit=10
        )
        self.assertEqual(coupon.code, 'TestCode')
        self.assertEqual(coupon.uses_limit, 10)


class CartProductTests(TestCase):
    """Test cart products"""

    def test_create_cart_product(self):
        user = create_user()
        category = models.Category.objects.create(
            name='Category1'
        )
        cart = models.Cart.objects.create(
            user=user
        )
        product = models.Product.objects.create(
            name='Product1',
            description='Product1 description',
            price=Decimal('5.50'),
            stock=10,
            is_hot=True,
            is_on_sale=False,
            category=category
        )
        cart_product = models.CartProduct.objects.create(
            cart=cart,
            product=product
        )
        self.assertEqual(cart_product.cart, cart)


class OrderTests(TestCase):
    """Test orders"""

    def test_create_order(self):
        user = create_user()
        order = models.Order.objects.create(
            status='pending',
            total_price=Decimal('5.50'),
            user=user
        )
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.total_price, Decimal('5.50'))
        self.assertEqual(order.user, user)


class OrderProductTests(TestCase):
    """Test order products"""

    def test_create_order_product(self):
        user = create_user()
        category = models.Category.objects.create(
            name='Category1'
        )
        order = models.Order.objects.create(
            status='pending',
            total_price=Decimal('5.50'),
            user=user
        )
        product = models.Product.objects.create(
            name='Product1',
            description='Product1 description',
            price=Decimal('5.50'),
            stock=10,
            is_hot=True,
            is_on_sale=False,
            category=category
        )
        order_product = models.OrderProduct.objects.create(
            order=order,
            product=product,
            quantity=2
        )
        self.assertEqual(order_product.order, order)
        self.assertEqual(order_product.product, product)
        self.assertEqual(order_product.quantity, 2)


class CommentTests(TestCase):
    """Test comments"""

    def test_create_comment(self):
        user = create_user()
        category = models.Category.objects.create(
            name='Category1'
        )
        post = models.Post.objects.create(
            title='Post1',
            content='Post1 content',
            user=user,
            category=category
        )
        comment = models.Comment.objects.create(
            content='Test comment',
            user=user,
            post=post
        )
        self.assertEqual(comment.content, 'Test comment')


class WeeklyDealTests(TestCase):
    """Test WeeklyDeal model"""

    def test_create_weekly_deal(self):
        category = models.Category.objects.create(
            name='Category1'
        )
        product = models.Product.objects.create(
            name='Product1',
            description='Product1 description',
            price=Decimal('5.50'),
            stock=10,
            is_hot=True,
            is_on_sale=False,
            category=category
        )
        weekly_deal = models.WeeklyDeal.objects.create(
            time=timezone.now(),
            product=product
        )
        self.assertEqual(weekly_deal.product, product)


class ServiceTests(TestCase):
    """Test Service model"""

    @patch('core.models.uuid.uuid4')
    def test_service_image_file_path(self, mock_uuid):
        """Test generating image path for service image"""

        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.service_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/service/{uuid}.jpg')

    def test_create_service(self):
        """Test creating service with image"""

        # Create a temporary image file
        image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')

        service = models.Service.objects.create(
            title='Service1',
            description='Service1 description',
            logo=image
        )
        self.assertEqual(service.title, 'Service1')
