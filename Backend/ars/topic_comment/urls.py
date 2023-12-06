from ars.comment import views
from ars.topic_comment import views
from django.urls import path

urlpatterns = [
    path('topic_comment/', views.Topic_Comment_Basic_View.as_view()),
    path('topic_comment/<id>/', views.Topic_Comment_One_View.as_view()),
    path('comment_topic/<topic_id>/', views.Comment_Top_View.as_view()),
    path('topic_comment_users/', views.Topic_Comment_User_View.as_view()),
    path('topic_comment_users/<id>/', views.Topic_Comment_ID_User_View.as_view())
]
