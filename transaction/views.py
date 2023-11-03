from datetime import timedelta
from django.utils import timezone

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.generics import UpdateAPIView
from rest_framework import generics
from rest_framework import exceptions, filters
from rest_framework.viewsets import ModelViewSet

from utils.exceptions import CustomException, fail, success
from .permissions import IsOwnerOrReadOnly

from .models import User, Contact,Transaction, Payment, Feedback
from .seializers import UserSerializer, validate_password, ContactSerializer, TransactionSerializer, PaymentSerializer, FeedbackSerializer


class SignupView(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                validate_email(email)
            except ValidationError as email_error:
                raise CustomException(
                    {"status": "Invalid email format", "detail": email_error.detail})

            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                raise CustomException(
                    {"status": "Username or email already in use"})
            user = serializer.create(serializer.validated_data)
            serializer = UserSerializer(user, context={'request': request})
            return Response(
                success(serializer.data),)
        raise CustomException(serializer.errors)


class LoginView(APIView):
    def post(self, request, format=None):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            validate_password(password)
            user = authenticate(username=username, password=password)

            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                expiration_date = token.created + timedelta(days=1)

                if expiration_date <= timezone.now():
                    token.delete()
                    token = Token.objects.create(user=user)

                user_serializer = UserSerializer(user)

                response_data = {
                    "token": token.key,
                    "user": user_serializer.data,
                }
                return Response(success(response_data))

            raise AuthenticationFailed("Invalid username or password")

        except Exception as e:
            raise CustomException(str(e))

class LogoutView(APIView):
    permission_classes = [HasAPIKey, IsAuthenticated]
    def post(self, request: Request, format=None) -> Response:
        try:
            token = request.user.auth_token
            token.delete()
            return Response(
                success("Logged out successfully"))
        except Exception as e:
            raise CustomException(str(e))
        
class UserProfileView(UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, HasAPIKey]
    def get_object(self):
        return self.request.user
    def update(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
            user, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            print(serializer.validated_data)
            self.perform_update(serializer)
            return Response(
                success(" Profile updated successfully"))
        except Exception as e:
            raise exceptions.APIException(str(e))

class ContactViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [HasAPIKey,IsOwnerOrReadOnly]

class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]    

class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]  

class TransactionHistoryView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['amount', 'category', 'due_date']

    def get_queryset(self):
        user = self.request.user
        transactions = Transaction.objects.filter(user=user)
        payments = Payment.objects.filter(transaction__user=user)
        return transactions, payments      

class FeedbackView(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Feedback.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)   