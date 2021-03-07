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

def jalali(datetime):
    return jdatetime.datetime.fromgregorian(
        datetime=datetime, 
        locale='fa_IR'
    ).strftime("%a، %d %b %Y، %H:%M")

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


@method_decorator(login_required(login_url='login'), name='dispatch')
class Logout(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='student')

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('login'))


@method_decorator(login_required(login_url='login'), name='dispatch')
class Dashboard(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.groups.filter(name='student')

    def get(self, request, *args, **kwargs):
        return render(
            request, 
            'student/dashboard.html', 
            {
                'data': {
                    'practices_count': Exercise.objects.all().count(),
                    'videos_count': Course.objects.all().count(),
                }
            }
        )

@method_decorator(login_required(login_url='login'), name='dispatch')
class CourseIndex(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='student')

    def get(self, request, *args, **kwargs):
        courses = Course.objects.all()
        for i in range(len(courses)):
            courses[i].created_at = jalali(courses[i].created_at)
            courses[i].owner_name = Teacher.objects.get(id=courses[i].owner_id)
        
        return render(
            request, 
            'student/course/index.html', 
            {
                'videos': courses
            }
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class CourseShow(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='student')

    def get(self, request, *args, **kwargs):
        course = Course.objects.get(id=kwargs['pk'])
        course.owner_name = Teacher.objects.get(id=course.owner_id)
        return render(
            request, 
            'student/course/detail.html', 
            {
                'video': course
            }
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class Exercise(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='student')

    def get(self, request, *args, **kwargs):
        exercises = Exercise.objects.all()
        student = Student.objects.get(user_id=request.user.id)
        for i in range(len(exercises)):
            exercises[i].deadline = jalali(exercises[i].deadline)
            exercises[i].created_at = jalali(exercises[i].created_at)
            exercises[i].owner_name = Teacher.objects.get(id=exercises[i].owmner_id)
            try:
                exercises[i].score = Answer.objects.get(
                    exercise_id=exercises[i].id, 
                    student_id=student.id
                ).score
                exercises[i].is_send_answer = True
            except ObjectDoesNotExist:
                exercises[i].is_send_answer = False

        return render(
            request, 
            'student/exercise/index.html', 
            {
                'practices': exercises
            }
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class ExerciseAnswer(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='student')

    def get(self, request, *args, **kwargs):
        excercise = Exercise.objects.get(id=kwargs['pk'])
        try:
            excercise.answer = Answer.objects.get(
                student_id=Student.objects.get(user_id=request.user.id).id,
                excercise_id=excercise.id
            ).file
            excercise.is_send_answer = True
        
        except ObjectDoesNotExist:
            excercise.is_send_answer = False
        
        excercise.due = jalali(excercise.due) 
        return render(
            request, 
            'student/excercise/answer.html', 
            {
                'practice': excercise
            }
        )

    def post(self, request, *args, **kwargs):
        ans = Answer(
            file=request.FILES['answerFile'], 
            student_id=Student.objects.get(user_id=request.user.id).id,
            excercise_id=kwargs['pk']
        )
        ans.save()
        return redirect(reverse('exercise-index'))
