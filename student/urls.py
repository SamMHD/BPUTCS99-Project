from django.urls import path

from .views import Practices, Dashboard, VideosList, VideosDetail, PracticeAnswer, Login, Logout

urlpatterns = [
    # authentication endpoints
    path('login', Login.as_view(), name='login'),
    path('logout', Logout.as_view(), name='logout'),

    # dashboard endpoint
    path('dashboard', Dashboard.as_view(), name='dashboard'),

    # course endpoints
    path('courses', VideosList.as_view(), name='course-index'),
    path('courses/<int:pk>', VideosDetail.as_view(), name='course-show'),

    # exercise endpoints
    path('exercises', Practices.as_view(), name='exercise-index'),
    path('exercises/<int:pk>', PracticeAnswer.as_view(), name='exercise-show'),
]
