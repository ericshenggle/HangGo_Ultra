from ars.comment import views
from ars.topic_like import views
from django.urls import path

urlpatterns = [
    path('topic_like/<id>/', views.Topic_Like_View.as_view()),
    path('topic_like/', views.Topic_Like_One_View.as_view()),
    path('topic_like_users/<id>/', views.Topic_Like_User_View.as_view()),
    path('topic_like_users_self/', views.Topic_Like_User_View_Self.as_view())
]
