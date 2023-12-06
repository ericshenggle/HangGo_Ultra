from rest_framework import routers
from ars.activity_type.views import type_views
from django.urls import include, path, re_path

# router = routers.DefaultRouter()
# router.register(r'activity', views.ActivityViewSet)
# router.register(r'activity_type', type_views.Activity_Type_View)

urlpatterns = [
    path('activity_types/', type_views.Activity_Type_Basic_View.as_view()),
    path('activity_types/<id>/', type_views.Activity_Type_One_View.as_view()),
    path('activity_types_list/',type_views.Activity_Type_List_View.as_view()),
    path('activity_types_user_list/',type_views.Activity_Type_User_Basic_View.as_view()),
]