from ars.select.views import Subscribe, SelectActivity, CancelSubscribe, CancelSelectActivity, RemarkActivity
from django.urls import path

urlpatterns = [
    path('subscribe', Subscribe.as_view()),
    path('select_activity', SelectActivity.as_view()),
    path('unsubscribe', CancelSubscribe.as_view()),
    path('cancel_activity', CancelSelectActivity.as_view()),
    path('remark_activity', RemarkActivity.as_view())
]
