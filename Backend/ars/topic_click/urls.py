from ars.comment import views
from ars.topic_click import views
from django.urls import path

urlpatterns = [
    path('topic_click/<id>/', views.Topic_Click_View.as_view()),
    path('topic_click/', views.Topic_Click_One_View.as_view()),
    path('topic_click_users/<id>/', views.Topic_Click_User_View.as_view()),
    path('topic_click_users_self/', views.Topic_Click_User_View_Self.as_view())
]
