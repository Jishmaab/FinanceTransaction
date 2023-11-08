from django.contrib.auth.password_validation import (CommonPasswordValidator,
                                                     MinimumLengthValidator,
                                                     NumericPasswordValidator)
from rest_framework import serializers

from .models import *
from .validators import (PasswordRegexValidation,
                         PasswordSpecialCharacterValidation)


class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.FileField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name',
                  'last_name', 'user_type', 'profile_picture']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        common_validator = CommonPasswordValidator()
        length_validator = MinimumLengthValidator(min_length=8)
        numeric_validator = NumericPasswordValidator()

        regex_validator = PasswordRegexValidation()
        special_char_validator = PasswordSpecialCharacterValidation()

        for validator in [common_validator, length_validator, numeric_validator, regex_validator, special_char_validator]:
            validator.validate(value, self.instance)

        return value

    def create(self, validated_data):
        user = User(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            user_type=validated_data.get('user_type'),
            profile_picture=validated_data.get('profile_picture')
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class TransactionHistorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    date = serializers.DateField()
    description = serializers.CharField(max_length=50)
    amount = serializers.IntegerField()
    balance = serializers.IntegerField()
    category = serializers.IntegerField()
    due_date = serializers.DateField()
    status = serializers.IntegerField()
