from rest_framework import routers
from ars.activity.views import activity_views, activity_schedule_views, condition_views, recommend_views, user_activities
from django.urls import include, path, re_path

urlpatterns = [
    path('activities/', activity_views.Activity_All_View.as_view()),
    path('activities/<id>/', activity_views.Activity_One_View.as_view()),

    path('condition/activities/', condition_views.condition_Act_View.as_view()),
    path('recommend/activities/', recommend_views.recommend_View.as_view()),
    path('activities_trend/', recommend_views.trend_View.as_view()),
    path('user_create_activities/<id>/', user_activities.User_Create_Activities.as_view()),
    path('user_create_activities_self/<id>/', user_activities.User_Create_Activities_Self.as_view())
]