# Django imports
from django.db import models
from django.contrib.auth.models import User

# Uncle imports
from teacher.models import Exercise

class Student(models.Model):
    # Identical Informations
    uni_id = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Answer(models.Model):
    # Identical Informations
    score = models.FloatField(null=True)
    student = models.ForeignKey(Student, default=1, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, default=1, on_delete=models.CASCADE)

    # Asset Informations
    file = models.FileField(upload_to='answers/')

    # Issuing Informations
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.practice)
