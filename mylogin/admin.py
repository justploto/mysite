from django.contrib import admin

# Register your models here.
from .models import User ,ConfirmString


class displayUser(admin.ModelAdmin):
    list_display = ('name','email','password','sex','c_time','has_confirmed')

admin.site.register(User, displayUser)

admin.site.register(ConfirmString)