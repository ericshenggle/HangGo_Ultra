from rest_framework import routers
from ars.activity_tag.views import tag_views
from django.urls import include, path, re_path

# router = routers.DefaultRouter()
# router.register(r'activity', views.ActivityViewSet)
# router.register(r'activity_type', type_views.Activity_Type_View)

urlpatterns = [
    path('tags', tag_views.Activity_Tag_Basic_View.as_view()),
    path('tags/<id>/', tag_views.Activity_Tag_One_View.as_view()),
    path('tags_list/', tag_views.Activity_Tag_List_View.as_view())

]