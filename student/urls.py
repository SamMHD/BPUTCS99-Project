from django.urls import path

from .views import Login, Logout, Dashboard, CourseIndex, CourseShow, ExerciseIndex, ExerciseShow

urlpatterns = [
    # authentication endpoints
    path(
        'login', 
        Login.as_view(), 
        name='login'
    ),
    path(
        'logout', 
        Logout.as_view(), 
        name='logout'
    ),

    # dashboard endpoint
    path(
        'dashboard', 
        Dashboard.as_view(), 
        name='dashboard'
    ),

    # course endpoints
    path(
        'courses', 
        CourseIndex.as_view(), 
        name='course-index'
    ),
    path(
        'courses/<int:pk>', 
        CourseShow.as_view(), 
        name='course-show'
    ),

    # exercise endpoints
    path(
        'exercises', 
        ExerciseIndex.as_view(), 
        name='exercise-index'
    ),
    path(
        'exercises/<int:pk>', 
        ExerciseShow.as_view(), 
        name='exercise-show'
    ),
]
