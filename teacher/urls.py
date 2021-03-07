from django.urls import path

from .views import Exercises, ExercisesAnswers, ExerciseCreate, ExerciseAnswerDetail,
from .views import CourcesList, CourcesDetail, CourseCreate
from .views import Login, Dashboard, Logout

urlpatterns = [
    # authentication endpoints
    path('login', Login.as_view(), name='teacher-login'),
    path('logout', Logout.as_view(), name='teacher-logout'),
    
    # dashboard endpoint
    path('dashboard', Dashboard.as_view(), name='teacher-dashboard'),

    # course endpoints
    path(
        'videos', 
        CourcesList.as_view(), 
        name='teacher-videos-list'
    ),
    path(
        'videos/<int:pk>', 
        CourcesDetail.as_view(), 
        name='videos-detail'
    ),
    path(
        'videos/create', 
        CourseCreate.as_view(), 
        name='video-create'
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
        ExerciseAnswerDetail.as_view(),
        name='exercises-answer-detail'
    ),
]
