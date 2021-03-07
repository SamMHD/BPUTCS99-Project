# Global imports
import datetime
import jdatetime

# Django imports
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

# Model imports
from django.contrib.auth.models import User
from .models import Exercise, Course, Teacher
from student.models import Answer, Student

def jalali(datetime):
    return jdatetime.datetime.fromgregorian(
        datetime=datetime, 
        locale='fa_IR'
    ).strftime("%a، %d %b %Y، %H:%M")


class Login(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('teacher-dashboard'))
        else:
            return render(request, 'teacher/login.html')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('teacher-dashboard'))
        else:
            form = request.POST
            try:
                username = get_object_or_404(User, email=form['email']).username
            except ObjectDoesNotExist:
                return render(request, 'teacher/login.html', {'error': 'invalid informations'})
            user = authenticate(username=username, password=form['password'])
            if user:
                login(request, user)
                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])
                else:
                    return redirect(reverse('teacher-dashboard'))
            else:
                return render(request, 'teacher/login.html', {'error': 'invalid informations'})


@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class Logout(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('teacher-login'))
