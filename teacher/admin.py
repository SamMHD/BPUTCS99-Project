from django.contrib import admin
from .models import Course, Exercise, Teacher
admin.site.register([Exercise, Course, Teacher])
