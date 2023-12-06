from ars.comment import views
from ars.topic_comment_like import views
from django.urls import path

urlpatterns = [
    path('topic_comment_like/<id>/', views.Topic_Comment_Like_View.as_view()),
    path('topic_comment_like/', views.Topic_Comment_Like_One_View.as_view()),
    path('topic_comment_like_users/<id>/', views.Topic_Comment_Like_User_View.as_view()),
    path('topic_comment_like_users_self/', views.Topic_Comment_Like_User_View_Self.as_view())
]
