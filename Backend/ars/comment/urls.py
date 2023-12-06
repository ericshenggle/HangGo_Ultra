from ars.comment import views 
from django.urls import path

urlpatterns = [
    path('comment/', views.Comment_Basic_View.as_view()),
    path('comment/<id>/', views.Comment_One_View.as_view()),
    path('comment_activities/<act_id>/', views.Comment_Act_View.as_view()),
    path('comment_users/', views.Comment_User_View.as_view())
]
