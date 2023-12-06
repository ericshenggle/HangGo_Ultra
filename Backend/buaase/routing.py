from channels.routing import ProtocolTypeRouter, URLRouter
from ars.talk_message.socket_url import websocket_url

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_url)
})
