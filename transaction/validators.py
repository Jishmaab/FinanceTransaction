from django.core.exceptions import ValidationError
import re

def validate_password(value):
    if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).{8,}$', value):
        raise ValidationError(
            "Password must contain at least 8 characters, "
            "including at least one lowercase letter, "
            "one uppercase letter, one digit, and one special character (@#$%^&+=)."
        )
