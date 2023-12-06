from ars.talk_message.views import MyMessage
from django.urls import path

urlpatterns = [
    path('mymessage/', MyMessage.as_view())
]
