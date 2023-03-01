from django.contrib import admin
from .models import Recipient, AppUser

admin.site.register(Recipient)
admin.site.register(AppUser)
