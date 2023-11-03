from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Contact)
admin.site.register(Payment)
admin.site.register(Feedback)
admin.site.register(Transaction)
admin.site.register(TransactionHistory)






