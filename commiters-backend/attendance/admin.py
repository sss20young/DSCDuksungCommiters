from django.contrib import admin
from .models import User, Repository

# Register your models here.
admin.sie.register(User)
admin.sie.register(Repository)