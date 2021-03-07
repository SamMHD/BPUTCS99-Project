from django.urls import path

from .views import Exercises, ExercisesAnswers, ExerciseCreate, ExerciseAnswerShow,
from .views import CourcesIndex, CourcesShow, CourseCreate
from .views import Login, Dashboard, Logout

urlpatterns = [
    # authentication endpoints
    path('login', Login.as_view(), name='teacher-login'),
    path('logout', Logout.as_view(), name='teacher-logout'),
    
    # dashboard endpoint
    path('dashboard', Dashboard.as_view(), name='teacher-dashboard'),

    # course endpoints
    path(
        'courses', 
        CourcesIndex.as_view(), 
        name='teacher-courses-list'
    ),
    path(
        'courses/<int:pk>', 
        CourcesShow.as_view(), 
        name='courses-detail'
    ),
    path(
        'courses/create', 
        CourseCreate.as_view(), 
        name='courses-create'
    ),
    
    # exercise endpoints
    path(
        'exercises', 
        Exercises.as_view(), 
        name='teacher-exercises-list'
    ),
    path(
        'exercises/create', 
        ExerciseCreate.as_view(), 
        name='exercise-create'
    ),
    path(
        'exercises/<int:pk>/answers', 
        ExercisesAnswers.as_view(),
        name='exercises-answers'
    ),
    path(
        'exercises/<int:exercise_id>/answers/<int:answer_id>', 
        ExerciseAnswerShow.as_view(),
        name='exercises-answer-show'
    ),
]
