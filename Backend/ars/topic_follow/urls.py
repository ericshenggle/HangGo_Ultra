from ars.comment import views
from ars.topic_follow import views
from django.urls import path

urlpatterns = [
    path('topic_follow/', views.Topic_Follow_One_View.as_view()),
    path('topic_follows/<id>/', views.Topic_Follow_View.as_view()),
    path('topic_follow_users/<id>/', views.Topic_Follow_User_View.as_view()),
    path('topic_follow_users_self/', views.Topic_Follow_User_View_Self.as_view())
]
