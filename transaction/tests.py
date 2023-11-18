from django.contrib.auth import get_user_model
from django.urls import reverse
from openpyxl import Workbook
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from .models import Contact, ExcelData, Feedback, Transaction


class LoginViewTests(APIRequestFactory):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.login_url = reverse('/api/login')

    def test_login_successful(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)

    def test_login_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('non_field_errors', response.data)

    def test_login_missing_credentials(self):
        data = {}
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('password', response.data)


class TransactionViewSetTests(APIRequestFactory):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.contact = Contact.objects.create(
            contact_name='Test Contact', user=self.user)

    def test_create_transaction(self):
        self.client.force_authenticate(user=self.user)
        transaction_data = {
            'user': self.user.id,
            'contact': self.contact.id,
            'amount': 100.00,
            'description': 'Test Transaction',
        }
        url = reverse('/api/transaction/')
        response = self.client.post(url, transaction_data, format='json')
        print(response.request)
        # print(response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.amount, transaction_data['amount'])
        self.assertEqual(transaction.description,
                         transaction_data['description'])
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.contact, self.contact)
        transaction.refresh_from_db()
        self.assertEqual(transaction.balance, self.user.profile.balance)


class ExcelUploadViewTests(APIRequestFactory):
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
            # url = reverse('excel-upload')
            data = {'file': excel_file}
            response = self.client.post('/api/upload/excel/', data, format='multipart')
            # print(response.content)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(ExcelData.objects.count(), 1)
            import os
            os.remove(excel_file_path)


class FeedbackViewTests(APIRequestFactory):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.staff_user = User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True)

    def test_list_feedback_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        Feedback.objects.create(
            title='Feedback 1', message='Message 1', user=self.user)
        Feedback.objects.create(
            title='Feedback 2', message='Message 2', user=self.staff_user)
        url = reverse('/api/feedback/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_feedback_count = Feedback.objects.count(
        ) if self.staff_user.is_staff else Feedback.objects.filter(user=self.staff_user).count()
        self.assertEqual(len(response.data), expected_feedback_count)

    def test_create_feedback_as_user(self):
        self.client.force_authenticate(user=self.user)
        feedback_data = {
            'title': 'Test Feedback',
            'message': 'This is a test feedback.',
        }
        url = reverse('/api/feedback/')
        response = self.client.post(url, feedback_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 1)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.title, feedback_data['title'])
        self.assertEqual(feedback.message, feedback_data['message'])
        self.assertEqual(feedback.user, self.user)

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.crypto import get_random_string

class SignupViewTestCase(APITestCase):
    def setUp(self):
        # Create a test user for login
        self.test_user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Password@123',
            first_name ='firstname',
            last_name ='lastname',
            user_type = 1,
            profile_picture =''
        )

    def test_signup_successful(self):
        url = '/api/signup/'
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password@123',
            'first_name':'firstname',
            'last_name':'lastname',
            'user_type': 1,  # Assuming 1 is a valid user type
            'profile_picture': self.generate_image_file()
        }

        response = self.client.post(url, data, format='multipart')
        # print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], True)
        # You can add more assertions based on your response structure

    def generate_image_file(self):
        # Generate a random image file for testing
        content = get_random_string(1024)  # 1024 bytes of random content
        return SimpleUploadedFile("test_image.jpg", content.encode(), content_type="image/jpeg")
