from ars.appealOrInform import views
from django.urls import path

urlpatterns = [
    path('appeal/', views.Appeal_View.as_view()),
    path('inform/', views.Inform_View.as_view()),
    path('appeal/<id>/', views.Appeal_One_View.as_view()),
    path('inform/<id>/', views.Inform_One_View.as_view()),
    path('appealSave/', views.Appeal_Save_View.as_view()),
    path('informSave/', views.Inform_Save_View.as_view()),
]
