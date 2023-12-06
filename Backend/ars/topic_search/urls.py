from django.urls import include, path, re_path
from ars.topic_search import views

urlpatterns = [
    path('topic_search/', views.Search_Topic.as_view()),
    path('topic_search_trend/', views.Search_Trend.as_view()),
    path('topic_search_history/', views.Search_His.as_view()),
    path('topic_search_historydel/',views.Search_His_Del.as_view())
]
