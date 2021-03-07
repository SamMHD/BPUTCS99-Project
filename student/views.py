# Global imports
import datetime
import jdatetime

# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import UserPassesTestMixin

# Model imports
from .models import Answer, Student
from teacher.models import Exercise, Teacher, Course

redirect_to_dashboard = redirect(reverse('dashboard'))

class Login(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'student/login.html')
        else:
            return redirect_to_dashboard
  
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect_to_dashboard
        else:
            data = request.POST
            try:
                username = User.objects.get(email = data['email']).username
            except ObjectDoesNotExist:
                return render(
                    request, 
                    'student/login.html', 
                    {
                        'error': 'Invalid Information'
                    }
                )

            user = authenticate(
                username=username, 
                password=data['password']
            )

            if user:
                login(request, user)
                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])
                else:
                    return redirect_to_dashboard
            else:
                return render(
                    request, 
                    'teacher/login.html', 
                    {
                        'error': 'Invalid Information'
                    }
                )


@method_decorator(login_required(login_url='student-login'), name='dispatch')
class Logout(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='student')

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('login'))
