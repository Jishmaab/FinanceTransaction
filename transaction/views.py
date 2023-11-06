from datetime import timedelta

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from rest_framework import exceptions, filters, generics
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from utils.exceptions import CustomException, fail, success

from .models import (Contact, Feedback, Payment, Transaction,
                     TransactionHistory, User)
from .permissions import IsOwnerOrReadOnly
from .seializers import (ContactSerializer, FeedbackSerializer,
                         PaymentSerializer, TransactionHistorySerializer,
                         TransactionSerializer, UserSerializer,
                         validate_password)


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
    permission_classes = [HasAPIKey, IsOwnerOrReadOnly]


class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        transaction = serializer.instance
        transaction.update_balance()


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
        payment = serializer.instance
        payment.update_transaction_balance()


class TransactionHistoryView(generics.ListAPIView):
    serializer_class = TransactionHistorySerializer
    filter_backends = [filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['amount', 'category', 'due_date']
    ordering_fields = ['date', 'amount', 'category', 'due_date']
    queryset = Transaction.objects.all()  

    def get_queryset(self):
        user = self.request.user
        transactions = Transaction.objects.filter(user=user)
        payments = Payment.objects.filter(transaction__user=user)
        history = []
        for transaction in transactions:
            history_entry = {
                'id': transaction.id,
                'date': transaction.date,
                'description': transaction.description,
                'amount': transaction.amount,
                'balance': transaction.balance,
                'category': transaction.category,
                'due_date': transaction.due_date,
            }
            transaction_history = TransactionHistory.objects.filter(
                transaction=transaction).first()
            if transaction_history:
                history_entry['status'] = transaction_history.status
            else:
                history_entry['status'] = None

            history.append(history_entry)

        return history


class FeedbackView(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [HasAPIKey,IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Feedback.objects.all()
        else:
            user = self.request.user
            return Feedback.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FeedbackResponseView(RetrieveUpdateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [HasAPIKey,IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Feedback.objects.filter(user=user)

    def perform_update(self, serializer):
        serializer.save(response=self.request.data.get('response'))
