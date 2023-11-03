from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class UserChoices(models.IntegerChoices):
        Admin = 0, 'Admin'
        User = 1, 'User'
    user_type = models.IntegerField(choices=UserChoices.choices, default=1)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'User'

class Contact(models.Model):
    class ContactChoices(models.IntegerChoices):
        individual  = 0, 'individual'
        entity = 1, 'entity'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=30, null=True, blank=True)
    contact_type = models.IntegerField(choices=ContactChoices.choices, default=0)

    class Meta:
        db_table = 'Contact'


class Transaction(models.Model):
    class CategoryChoices(models.IntegerChoices):
        debit  = 0, 'debit'
        credit = 1, 'credit'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=50, null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    balance = models.IntegerField(null=True, blank=True)
    category = models.IntegerField(choices=CategoryChoices.choices, default=0)
    due_date = models.DateField(null=True, blank=True)
    class Meta:
        db_table = 'Transaction'

class Payment(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)    
    payment_date = models.DateField(null=True, blank=True)
    paid_amount = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'Payment'

class TransactionHistory(models.Model):
    class StatusChoices(models.IntegerChoices):
        completed = 0, 'completed '
        pending = 1, 'pending'
    transaction = models.OneToOneField(User,on_delete=models.CASCADE)
    status = models.IntegerField(choices=StatusChoices.choices, default=0) 
    class Meta:
        db_table = 'TransactionHistory'

class Feedback(models.Model):
    class FeedbackChoices(models.IntegerChoices):
        opened = 0, 'opened'
        inprogress = 1, 'inprogress'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20, null=True, blank=True)
    message = models.CharField(max_length=40, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True,blank=True)
    status_type = models.IntegerField(choices=FeedbackChoices.choices, default=1) 
    response = models.CharField(max_length=40, null=True, blank=True)
    class Meta:
        db_table = 'Feedback'



