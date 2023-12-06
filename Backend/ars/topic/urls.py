from rest_framework import routers
from ars.activity.views import activity_views, activity_schedule_views, condition_views, recommend_views, \
    user_activities
from django.urls import include, path, re_path
from ars.topic.views import topic_view, condition_views,user_topic
# router = routers.DefaultRouter()
# router.register(r'activity', views.ActivityViewSet)
# router.register(r'activity_type', type_views.Activity_Type_View)

urlpatterns = [
    path('topic/', topic_view.Topic_All_View.as_view()),
    path('topic/<id>/', topic_view.Topic_One_View().as_view()),
    # path('schedule/activities/', activity_schedule_views.Activity_Schedule_View.as_view()),
    # path('schedule/user_activities/', activity_schedule_views.Activity_User_Schedule_View.as_view()),

    path('condition/topics/', condition_views.condition_Top_View.as_view()),
    #path('activities_trend/', recommend_views.trend_View.as_view()),
    path('user_create_topic/<id>/', user_topic.User_Create_Topic.as_view()),
    path('user_create_topic_self/', user_topic.User_Create_Topic_Self.as_view()),
    # path('normal_activities/', activity_views.Normal_Activity_Basic_View.as_view()),
    # path('normal_activities/<id>/', activity_views.Normal_Activity_One_View.as_view()),

    # path('lectures/', activity_views.Lecture_Basic_View.as_view()),
    # path('lectures/<id>/', activity_views.Lecture_One_View.as_view()),
]