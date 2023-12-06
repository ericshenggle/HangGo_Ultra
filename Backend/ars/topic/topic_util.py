import re
import pytz
from rest_framework import serializers
import ars.models
time_format = "%Y/%m/%d %H:%M"
import io


class MyDateTimeField(serializers.DateTimeField):
    def __init__(self, *args, **kwargs):
        super(MyDateTimeField, self).__init__(format=time_format, *args, **kwargs)


def verify_activity(data):
    message = ""
    error = 0
    if data['start_at'] >= data['end_at']:
        error = 1
        message = '活动开始时间应小于活动结束时间'
    elif data['activity']['start_enrollment_at'] >= data['activity']['end_enrollment_at']:
        error = 1
        message = '活动报名开始时间应小于活动报名结束时间'
    elif data['start_at'] <= data['activity']['end_enrollment_at']:
        error = 1
        message = '活动报名时间应大于活动报名结束时间'
    elif 'tags' in data['activity']:
        if len(data['activity']['tags']) > 5:
            error = 1
            message = '活动标签数目超过5个'
        for k in data['activity']['tags']:
            if len(k['name']) > 10:
                error = 1
                message = '标签长度过长'
    if len(data['activity']['name']) >= 50:
        error = 1
        message = '活动名长度过长'
    elif int(data['allow_total']) >= 10000000:
        error = 1
        message = '参与人数过多'
        # if 'photo' in data['activity']:# and type(data['activity']['photo']) == io.BufferedRandom:
    #     error = 1
    #     # message = '不能上传动图'
    #     message = type(data['activity']['photo'])

    if len(data['description']) > 200:
        error = 1
        message = '活动描述过长'

    if data['activity']['name'].strip() == '':
        error = 1
        message = '活动名不能为空'
    if data['description'].strip() == '':
        error = 1
        message = '描述不能为空'
    if data['activity']['position'].strip() == '':
        error = 1
        message = '具体地点不能为空'

    if error == 1:
        return {'error': 1, 'message': message}
    return {}


def change_Activity_format(request):
    data = request.data.copy()
    new_data = {}
    new_data['start_at'] = data['start_at']
    new_data['end_at'] = data['end_at']
    new_data['description'] = data['description']
    new_data['allow_total'] = data['allow_total']
    new_data['activity'] = {}
    new_data['activity']['name'] = data['name']
    new_data['activity']['start_enrollment_at'] = data['start_enrollment_at']
    new_data['activity']['end_enrollment_at'] = data['end_enrollment_at']
    new_data['activity']['location'] = data['location']
    new_data['activity']['position'] = data['position']

    verify_null(data)

    if 'latitude' in data and data['latitude'] != '':
        new_data['activity']['latitude'] = data['latitude']
    else:
        new_data['activity']['latitude'] = None
    if 'longitude' in data and data['longitude'] != '':
        new_data['activity']['longitude'] = data['longitude']
    else:
        new_data['activity']['longitude'] = None
    if 'photo' in data:
        new_data['activity']['photo'] = data['photo']
    else:
        new_data['activity']['photo'] = None
    if 'activity_type' in data:
        new_data['activity']['activity_type'] = {'name': data['activity_type']}
    if 'tags' in data:
        tags = data['tags'].split()
        new_data['activity']['tags'] = []
        for i in tags:
            new_data['activity']['tags'].append({'name': i})

    return new_data


def verify_null(data):
    can_null = ['tags', 'activity_type', 'photo', 'latitude', 'longitude']
    for key, val in zip(data.keys(), data.values()):
        if key in can_null:
            continue
        if val == "" or val == None:
            raise KeyError


def change_Topic_format(request):
    data = request.data.copy()
    new_data = {}
    new_data['description'] = data['description']
    new_data['topic'] = {}
    new_data['topic']['topic_type'] = data['topic_type']
    new_data['topic']['audit'] = ars.models.Topic.AuditStatusChoice.审核通过
    new_data['topic']['name'] = data['name']
    verify_null(data)

    if 'photo' in data:
        new_data['topic']['photos'] = data['photo']
    else:
        new_data['topic']['photos'] = None

    return new_data