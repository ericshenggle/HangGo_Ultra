from rest_framework import routers
from ars.activity_message.message_views import Activity_Message_View
from django.urls import include, path, re_path

# router = routers.DefaultRouter()
# router.register(r'activity', views.ActivityViewSet)
# router.register(r'activity_type', type_views.Activity_Type_View)

urlpatterns = [
    path('activity_messages/', Activity_Message_View.as_view()),
    
]