from ars.bykchandler.views import UpdateUserBykc, UpdateBykc
from django.urls import path

urlpatterns = [
    path('update_user_bykc', UpdateUserBykc.as_view()),
    path('update_bykc', UpdateBykc.as_view())
]
