from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from product.models import Category, Product
from users.models import CustomUser
from users.serializers import CustomTokenObtainPairSerializer


class ProductAgeValidationTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.url = reverse("product-list-create")

    def get_access_token(self, user):
        token = CustomTokenObtainPairSerializer.get_token(user)
        return str(token.access_token)

    def test_product_creation_requires_birthdate_in_token(self):
        user = CustomUser.objects.create_user(
            email="missing-birthdate@example.com",
            password="password123",
            birthdate=None,
            is_active=True,
        )
        token = CustomTokenObtainPairSerializer.get_token(user)
        payload = token.payload
        payload.pop("birthdate", None)
        access_token = str(token.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(
            self.url,
            {
                "title": "Phone",
                "description": "Great phone",
                "price": 100.0,
                "category": self.category.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Укажите дату рождения, чтобы создать продукт.", response.data["non_field_errors"])

    def test_product_creation_rejects_underage_user(self):
        user = CustomUser.objects.create_user(
            email="underage@example.com",
            password="password123",
            birthdate=date.today().replace(year=date.today().year - 17),
            is_active=True,
        )
        access_token = self.get_access_token(user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(
            self.url,
            {
                "title": "Phone",
                "description": "Great phone",
                "price": 100.0,
                "category": self.category.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Вам должно быть 18 лет, чтобы создать продукт.", response.data["non_field_errors"])

    def test_product_creation_allows_adult_user(self):
        user = CustomUser.objects.create_user(
            email="adult@example.com",
            password="password123",
            birthdate=date.today().replace(year=date.today().year - 20),
            is_active=True,
        )
        access_token = self.get_access_token(user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(
            self.url,
            {
                "title": "Phone",
                "description": "Great phone",
                "price": 100.0,
                "category": self.category.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(title="Phone").exists())
