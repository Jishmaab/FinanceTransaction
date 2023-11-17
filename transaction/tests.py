# from django.core.exceptions import ValidationError
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase

# from .models import User
# import os
# from django.core.files.uploadedfile import SimpleUploadedFile

# class SignupViewTests(APITestCase):
# fixtures = ['transaction/fixtures/users.json']

# def test_signup_successful(self):
#     url = reverse('signup')

#     # Correctly construct the file path
#     file_path = "finance/media/profile_pictures/fem2.jpg"

#     with open(file_path, "rb") as image_file:
#         binary_data = image_file.read()

#     image = SimpleUploadedFile("fem2.jpg", binary_data, content_type="image/jpeg")

#     data = {
#         'username': 'newuser',
#         'email': 'newuser@example.com',
#         'password': 'testpassword',
#         'profile_picture': image,
#     }

#     response = self.client.post(url, data, format='json')
#     print(response.content)

#     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#     self.assertEqual(User.objects.count(), 2)
#     self.assertEqual(User.objects.get(username='newuser').username, 'newuser')

#   def test_signup_existing_user(self):
#     url = reverse('signup')
#     with open("media/profile_pictures/fem2.jpg", "rb") as image_file:
#         binary_data = image_file.read()

#     image = SimpleUploadedFile("fem2.jpg", binary_data, content_type="image/jpeg")

#     data = {
#         'username': 'alice45',
#         'email': 'alice456@gmail.com',
#         'password': 'Alice@2023',
#         'profile_picture': image,
#     }

#     response = self.client.post(url, data, format='json')

#     # Check if the response content type is not binary
#     if 'image/jpeg' not in response['content-type']:
#         # If it's not binary, print the content as UTF-8
#         print(response.content.decode('utf-8'))
#     else:
#         # If it is binary, handle it accordingly (e.g., save to a file)
#         with open('output_image.jpg', 'wb') as output_file:
#             output_file.write(response.content)

#     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     self.assertIn('Username or email already in use', response.data['error'])


# class LoginViewTests(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser',
#             password='testpassword'
#         )
#         self.login_url = reverse('login')

#     def test_login_successful(self):
#         data = {
#             'username': 'testuser',
#             'password': 'testpassword',
#         }
#         response = self.client.post(self.login_url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('token', response.data)
#         self.assertIn('user', response.data)

#     def test_login_invalid_credentials(self):
#         data = {
#             'username': 'testuser',
#             'password': 'wrongpassword',
#         }
#         response = self.client.post(self.login_url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertIn('non_field_errors', response.data)

#     def test_login_missing_credentials(self):
#         data = {}
#         response = self.client.post(self.login_url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('username', response.data)
#         self.assertIn('password', response.data)

# from rest_framework import status
# from django.urls import reverse
# from .models import Transaction
# # from .serializers import TransactionSerializer
# from django.contrib.auth.models import User
# from rest_framework.test import APIRequestFactory
# from rest_framework.test import APITestCase
# from .models import *
# from rest_framework.test import APITestCase, APIRequestFactory
# from rest_framework import status
# from django.urls import reverse
# from django.contrib.auth import get_user_model
# from .models import Transaction, Contact
# class TransactionViewSetTests(APITestCase):
#     def setUp(self):
#         # Create a user and a contact for testing
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.contact = Contact.objects.create(contact_name='Test Contact', user=self.user)

#     def test_create_transaction(self):
#         # Log in the user
#         self.client.force_authenticate(user=self.user)

#         # Define transaction data
#         transaction_data = {
#             'user': self.user.id,
#             'contact': self.contact.id,
#             'amount': 100.00,
#             'description': 'Test Transaction',
#         }

#         # Get the URL for creating a transaction
#         url = reverse('transaction-list')

#         # Make a POST request to create a transaction
#         response = self.client.post(url, transaction_data, format='json')
#         print(response.status_code)
#         print(response.content)

#         # Check that the response status code is 201 (created)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         # Check that the transaction was created in the database
#         self.assertEqual(Transaction.objects.count(), 1)

#         # Check that the transaction data matches the provided data
#         transaction = Transaction.objects.first()
#         self.assertEqual(transaction.amount, transaction_data['amount'])
#         self.assertEqual(transaction.description, transaction_data['description'])

#         # Check that the user and contact associated with the transaction are correct
#         self.assertEqual(transaction.user, self.user)
#         self.assertEqual(transaction.contact, self.contact)

#         # Check that the balance is updated
#         transaction.refresh_from_db()
#         self.assertEqual(transaction.balance, self.user.profile.balance)

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from openpyxl import Workbook
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.test import APITestCase

from .models import ExcelData


class ExcelUploadViewTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_upload_excel_file(self):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append(['order_date', 'order_quantity', 'sales', 'ship_mode',
                         'unit_price', 'customer_name', 'customer_segment', 'product_category'])
        worksheet.append(['2023-01-01', 10, 100.0, 'Air', 5.0,
                         'John Doe', 'Segment', 'Category'])
        excel_file_path = "test_excel_file.xlsx"
        workbook.save(excel_file_path)
        with open(excel_file_path, 'rb') as excel_file:
            url = reverse('excel-upload')
            data = {'file': excel_file}
            response = self.client.post(url, data, format='multipart')
            # print(response.content)
            # self.assertEqual(response.status_code, status.HTTP_200_OK)
            # self.assertEqual(ExcelData.objects.count(), 1)
            import os

            # os.remove(excel_file_path)
