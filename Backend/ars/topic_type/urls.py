from rest_framework import routers
from ars.topic_type.views import type_views
from django.urls import include, path, re_path

# router = routers.DefaultRouter()
# router.register(r'activity', views.ActivityViewSet)
# router.register(r'activity_type', type_views.Activity_Type_View)

urlpatterns = [
    path('topic_types/', type_views.Topic_Type_Basic_View.as_view()),
    path('topic_types/<id>/', type_views.Topic_Type_One_View.as_view()),
    path('topic_types_simple/', type_views.Topic_Type_List_View.as_view()),
]