from rest_framework import serializers

time_format = "%Y/%m/%d %H:%M"


class MyDateTimeField(serializers.DateTimeField):
    def __init__(self, *args, **kwargs):
        super(MyDateTimeField, self).__init__(format=time_format, *args, **kwargs)


def verify_commission(data):
    message = ""
    error = 0
    if data['start_time'] >= data['end_time']:
        error = 1
        message = '委托开始时间应小于委托结束时间'
    elif 'tags' in data.keys():
        if len(data['tags']) > 5:
            error = 1
            message = '委托标签数目超过5个'
        for k in data['tags']:
            if len(k['name']) > 10:
                error = 1
                message = '标签长度过长'
    if len(data['name']) >= 50:
        error = 1
        message = '委托名长度过长'

    if len(data['description']) > 200:
        error = 1
        message = '委托描述过长'

    try:
        if int(data['fee']) < 0:
            error = 1
            message = '佣金数量填写错误'
    except ValueError:
        error = 1
        message = '佣金填写错误'

    if error == 1:
        return {'error': 1, 'message': message}
    return {}


def verify_null(data):
    can_null = ['tags', 'comment', 'accepted_user']
    for key, val in zip(data.keys(), data.values()):
        if key in can_null:
            continue
        if val == "" or val == None:
            raise KeyError

