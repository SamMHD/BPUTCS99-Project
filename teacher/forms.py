from django import forms
from .models import Exercise
from django.forms import ModelForm

class CreateExerciseForm(ModelForm):
    class Meta:
        model = Exercise
        fields = '__all__'
