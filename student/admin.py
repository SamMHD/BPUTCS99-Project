from django.contrib import admin
from .models import Answer, Student
admin.site.register([Answer, Student])