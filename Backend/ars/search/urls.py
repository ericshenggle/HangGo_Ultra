from ars.search.views import Search, Search_Trend, Search_His
from django.urls import include, path, re_path

urlpatterns = [
    path('search/', Search.as_view()),
    path('search_trending/', Search_Trend.as_view()),
    path('search_history/', Search_His.as_view()),
]
