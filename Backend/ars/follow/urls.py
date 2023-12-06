from ars.follow.views import Followees,Followers
from django.urls import path

urlpatterns = [
    path('followers', Followers.as_view()),
    path('followees', Followees.as_view()),
]
