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


@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class Dashboard(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get(self, request, *args, **kwargs):
        owner_id = get_object_or_404(Teacher, user_id=request.user.id).id
        data = {
            'practices_count': Exercise.objects.filter(owner_id=owner_id).count(),
            'videos_count': Course.objects.filter(owner_id=owner_id).count(),
            'students_count': Student.objects.all().count(),
        }
        return render(request, 'teacher/dashboard.html', {'data': data})



@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class Exercise(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get(self, request, *args, **kwargs):
        owner_id = get_object_or_404(Teacher, user_id=request.user.id).id
        exercises = Exercise.objects.filter(owner_id=owner_id)
        for i in range(len(exercises)):
            exercises[i].due = jalali(exercises[i].due)
            exercises[i].created_at = jalali(exercises[i].created_at)
        return render(
            request, 
            'teacher/exercise/index.html',
            {
                'practices': exercises
            }
        )


@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class ExerciseCreate(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get(self, request, *args, **kwargs):
        if 'date_error' in kwargs:
            return render(request, 'teacher/exercise/create.html', {'date_error': kwargs['date_error']})
        return render(request, 'teacher/exercise/create.html')

    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            date = list(map(int, data['date'].split("/")))
            time = list(map(int, data['time'].split(":")))
            g_datetime = jdatetime.datetime(
                date[0], date[1], date[2], time[0], time[1]).togregorian()
        except:
            kwargs['date_error'] = 'invalid date and time'
            return self.get(request, *args, **kwargs)
        exercise = Exercise(
            title=data['title'], comment=data['comment'], deadline=g_datetime)
        exercise.save()
        return redirect(reverse('teacher-exercises-index'))

@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class ExercisesAnswers(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get(self, request, *args, **kwargs):
        owner_id = get_object_or_404(Teacher, user_id=request.user.id).id
        exercise = get_object_or_404(Exercise, id=kwargs['pk'])
        if exercise.onwer_id != owner_id:
            raise PermissionDenied()
        answers = Answer.objects.filter(exercise_id=kwargs['pk'])
        for i in range(len(answers)):
            answers[i].created_at = jalali(answers[i].created_at)
            answers[i].student = get_object_or_404(Student, id=answers[i].student_id)
        return render(
            request, 
            'teacher/exercise/answers.html', 
            {
                'answers': answers, 'practice_title': exercise.title
            }
        )


@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class ExercisesAnswerShow(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get_query(self, request, exercise_id, answer_id):
        answer = get_object_or_404(Answer, id=answer_id)
        answer.created_at = jalali(answer.created_at)
        answer.student = get_object_or_404(Student, id=answer.student_id)
        student = get_object_or_404(Student, id=answer.student_id)
        
        owner_id = get_object_or_404(Teacher, user_id=request.user.id).id
        exercise = get_object_or_404(Exercise, id=exercise_id, owner_id=owner_id)
        exercise.due = jalali(exercise.due)
        return (answer, exercise, student)

    def get(self, request, *args, **kwargs):
        (answer, exercise, student) = self.get_query(request, exercise_id=kwargs['practice_id'], answer_id=kwargs['answer_id'])
        template_data = {
            'answer': answer,
            'practice': exercise,
            'student': student
        }
        if 'score_error' in kwargs:
            template_data['score_error'] = kwargs['score_error']
        return render(
            request,
            'teacher/exercise/answer-detail.html', 
            template_data
        )

    def post(self, request, *args, **kwargs):
        score = request.POST['score']
        if not self.validate_score(score):
            kwargs['score_error'] = 'score is invalid'
            return self.get(request, *args, **kwargs)
        exercise_id = kwargs['practice_id']

        answer = get_object_or_404(Answer, id=kwargs['answer_id'])
        answer.score = score
        answer.save()

        return redirect(reverse('exercises-answers', kwargs={'pk': exercise_id}))

    def validate_score(self, score):
        try:
            val = float(score)
            return True
        except ValueError:
            return False



@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class Exercise(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get(self, request, *args, **kwargs):
        owner_id = get_object_or_404(Teacher, user_id=request.user.id).id
        exercises = Exercise.objects.filter(owner_id=owner_id)
        for i in range(len(exercises)):
            exercises[i].due = jalali(exercises[i].due)
            exercises[i].created_at = jalali(exercises[i].created_at)
        return render(
            request, 
            'teacher/exercise/index.html',
            {
                'practices': exercises
            }
        )


@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class ExerciseCreate(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get(self, request, *args, **kwargs):
        if 'date_error' in kwargs:
            return render(request, 'teacher/exercise/create.html', {'date_error': kwargs['date_error']})
        return render(request, 'teacher/exercise/create.html')

    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            date = list(map(int, data['date'].split("/")))
            time = list(map(int, data['time'].split(":")))
            g_datetime = jdatetime.datetime(
                date[0], date[1], date[2], time[0], time[1]).togregorian()
        except:
            kwargs['date_error'] = 'invalid date and time'
            return self.get(request, *args, **kwargs)
        exercise = Exercise(
            title=data['title'], comment=data['comment'], deadline=g_datetime)
        exercise.save()
        return redirect(reverse('teacher-exercises-index'))

@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class ExercisesAnswers(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get(self, request, *args, **kwargs):
        owner_id = get_object_or_404(Teacher, user_id=request.user.id).id
        exercise = get_object_or_404(Exercise, id=kwargs['pk'])
        if exercise.onwer_id != owner_id:
            raise PermissionDenied()
        answers = Answer.objects.filter(exercise_id=kwargs['pk'])
        for i in range(len(answers)):
            answers[i].created_at = jalali(answers[i].created_at)
            answers[i].student = get_object_or_404(Student, id=answers[i].student_id)
        return render(
            request, 
            'teacher/exercise/answers.html', 
            {
                'answers': answers, 'practice_title': exercise.title
            }
        )


@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class ExercisesAnswerShow(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get_query(self, request, exercise_id, answer_id):
        answer = get_object_or_404(Answer, id=answer_id)
        answer.created_at = jalali(answer.created_at)
        answer.student = get_object_or_404(Student, id=answer.student_id)
        student = get_object_or_404(Student, id=answer.student_id)
        
        owner_id = get_object_or_404(Teacher, user_id=request.user.id).id
        exercise = get_object_or_404(Exercise, id=exercise_id, owner_id=owner_id)
        exercise.due = jalali(exercise.due)
        return (answer, exercise, student)

    def get(self, request, *args, **kwargs):
        (answer, exercise, student) = self.get_query(request, exercise_id=kwargs['practice_id'], answer_id=kwargs['answer_id'])
        template_data = {
            'answer': answer,
            'practice': exercise,
            'student': student
        }
        if 'score_error' in kwargs:
            template_data['score_error'] = kwargs['score_error']
        return render(
            request,
            'teacher/exercise/answer-detail.html', 
            template_data
        )

    def post(self, request, *args, **kwargs):
        score = request.POST['score']
        if not self.validate_score(score):
            kwargs['score_error'] = 'score is invalid'
            return self.get(request, *args, **kwargs)
        exercise_id = kwargs['practice_id']

        answer = get_object_or_404(Answer, id=kwargs['answer_id'])
        answer.score = score
        answer.save()

        return redirect(reverse('exercises-answers', kwargs={'pk': exercise_id}))

    def validate_score(self, score):
        try:
            val = float(score)
            return True
        except ValueError:
            return False


@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class CoursesIndex(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get(self, request, *args, **kwargs):
        owner_id = get_object_or_404(Teacher, user_id=request.user.id).id
        courses = Course.objects.filter(owner_id=owner_id)
        for i in range(len(courses)):
            courses[i].created_at = jalali(courses[i].created_at)
        return render(request, 'teacher/course/index.html', {'videos': courses})


@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class CourseCreate(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get(self, request, *args, **kwargs):
        if 'video_error' in kwargs:
            return render(request, 'teacher/course/create.html', {'video_error': kwargs['video_error']})
        return render(request, 'teacher/course/create.html')

    def post(self, request, *args, **kwargs):
        data = request.POST
        video = request.FILES['video']
        print(video.size)
        if video.content_type.find('course/') == -1:
            kwargs['video_error'] = "wrong format"
            return self.get(request, *args, **kwargs)
        if video.size > settings.MAX_UPLOAD_SIZE * 1000 * 1000:
            kwargs['video_error'] = "video size must be less than 10mg"
            return self.get(request, *args, **kwargs)
        course = Course(title=data['title'], video=video)
        course.save()
        return redirect(reverse('teacher-courses-index'))

@method_decorator(login_required(login_url='teacher-login'), name='dispatch')
class CoursesShow(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='teacher')

    def get(self, request, *args, **kwargs):
        owner_id = get_object_or_404(Teacher, user_id=request.user.id).id
        course = get_object_or_404(Course, id=kwargs['pk'], owner_id=owner_id)
        return render(request, 'teacher/course/detail.html', {'video': course})

