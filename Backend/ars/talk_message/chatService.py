import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from channels.generic.websocket import WebsocketConsumer
from rest_framework.authtoken.models import Token
from ars.models import TalkMessage, User
from ars.notification.wxapi import *
import json

# 这里除了 WebsocketConsumer 之外还有
# JsonWebsocketConsumer
# AsyncWebsocketConsumer
# AsyncJsonWebsocketConsumer
# WebsocketConsumer 与 JsonWebsocketConsumer 就是多了一个可以自动处理JSON的方法
# AsyncWebsocketConsumer 与 AsyncJsonWebsocketConsumer 也是多了一个JSON的方法
# AsyncWebsocketConsumer 与 WebsocketConsumer 才是重点
# 看名称似乎理解并不难 Async 无非就是异步带有 async / await
# 是的理解并没有错,但对与我们来说他们唯一不一样的地方,可能就是名字的长短了,用法是一模一样的
# 最夸张的是,基类是同一个,而且这个基类的方法也是Async异步的
user_dict = {}
access_key = "LTAI5tLTQeSKP2iH3tdw8tRR"
access_secret = "vntpXeVP9WTxISlqU7Xeq7XZuktjjf"


def chatrobot(content):
    client = AcsClient(
        access_key,
        access_secret,
        "cn-shanghai"
    )
    commonRequest = CommonRequest()
    commonRequest.set_product("Chatbot")
    commonRequest.set_method("GET")
    commonRequest.add_query_param("InstanceId", "chatbot-cn-EZRQmFn7ea")
    commonRequest.add_query_param("Utterance", content)
    commonRequest.set_domain("chatbot.cn-shanghai.aliyuncs.com")
    commonRequest.set_action_name("Chat")
    commonRequest.set_version("2017-10-11")
    commonRequest.set_accept_format("json")
    commonResponse = client.get_response(commonRequest)
    answer = str(commonResponse[2], encoding='utf-8')
    s1 = json.loads(answer)
    return s1['Messages'][0]['Text']['Content']


def chatrobot2(content):
    response = requests.get(f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={content}")
    return response.json()['content']


class ChatService(WebsocketConsumer):
    # 当Websocket创建连接时
    def connect(self):
        token = self.scope.get("url_route").get("kwargs").get("token")
        try:
            tk_object = Token.objects.get(key=token)
        except Token.DoesNotExist:
            self.close()
            return
        self.accept()
        from_user_id = tk_object.user.id
        user_dict[from_user_id] = self

    # 当Websocket接收到消息时
    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        request_type = data.get('type', '')
        if request_type == 'send_message':
            ack_number = data.get('ack_number')
            to_user = data.get('to_user')
            token = self.scope.get("url_route").get("kwargs").get("token")
            try:
                tk_object = Token.objects.get(key=token)
            except Token.DoesNotExist:
                return
            try:
                target_user = User.objects.get(pk=to_user)
            except User.DoesNotExist:
                return
            message = data.get('message')
            tkmessage = TalkMessage(content=message, from_user=tk_object.user, to_user=target_user)
            tkmessage.save()
            send_Chat_to_user(tkmessage)
            self.send('{{ack_sent:{0}}}'.format(ack_number))
            ws = user_dict.get(to_user, None)
            if ws is not None:
                ws.send('newdata')
        elif request_type == 'ack_receive':
            message_id = data.get('message_id', '')
            try:
                tkmessage = TalkMessage.objects.get(pk=message_id)
            except TalkMessage.DoesNotExist:
                return
            tkmessage.delete()
        elif request_type == 'chat_robot':
            ret_answer = {"robot": chatrobot2(data.get('message'))}
            self.send(json.dumps(ret_answer))
        elif request_type == 'ping':
            self.send('pong')

    # 当Websocket发生断开连接时
    def disconnect(self, code):
        pass


def __init__():
    chatrobot('123')
