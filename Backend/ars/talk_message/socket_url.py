from django.urls import path
from ars.talk_message.chatService import ChatService

websocket_url = [
    path("talk_message/<token>/", ChatService.as_asgi())
]
