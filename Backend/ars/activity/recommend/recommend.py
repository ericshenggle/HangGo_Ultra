from django.contrib.auth.models import User, Group
from django.db.models import Count
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi

from ars.activity.serializers.activity_info_serializer import ActivityInfo_Serializer
from ars.activity.serializers.activity_serializers import *
from ars.activity.serializers.activity_change_serializers import *
from ars.activity.serializers.activity_get_serializer import *
# from ars.activity.serializers.lecture_serializer import Lecture_Serializer
from ars.activity_type.serializers import *
from ars.models import *

from ars.utils import change_data_time_format
from datetime import *
from functools import cmp_to_key
from collections import Counter
import math

def cmp(x, y):
    return y[1] - x[1] 

def recommend_activity(user):
    now = datetime.now()
    all_user = User.objects.all()
    sim = {}
    sim_list = []
    for u in all_user:
        if u.id == 1:
            continue
        elif u.id == user.id:
            continue
        res = calc_sim(user, u)
        sim[u.id] = res
        sim_list.append((u, res))
    sim_list.sort(key=cmp_to_key(cmp))

    sim_users = sim_list[:10]

    attend_activty_list = user.attend_activities.all()
    type_score = get_type_score(user)

    recommend_activity_dict = {}

    for sim_user, ss in sim_users:
        sim_activity_list = sim_user.attend_activities.all()
        for act in sim_activity_list:
            if act in attend_activty_list:
                continue
            type_s = 0.
            if act.activity_type.id in type_score:
                type_s = type_score[act.activity_type.id]
            #now_ = now.replace(tzinfo=pytz.timezone('UTC'))
            if act.end_enrollment_at >= now:
                if act.id not in recommend_activity_dict:
                    recommend_activity_dict[act.id] = [act, sim[sim_user.id]*math.exp((type_s-0.5)/5)]
    
    try:
        l_m = sum([i[1] for i in recommend_activity_dict.values()]) / len(recommend_activity_dict.keys())
    except ZeroDivisionError:
        l_m = 1

    for type_id in type_score.keys():
        activity_type = ActivityType.objects.get(id=type_id)
        type_activities = activity_type.type_activities.filter(audit_status=3)
        t_s = type_score[type_id]
        for idx, t_a in enumerate(type_activities):
            score = 2.5
            # now_ = now.replace(tzinfo=pytz.timezone('UTC'))
            if t_a.end_enrollment_at >= now:
                if t_a.id not in recommend_activity_dict:
                    recommend_activity_dict[t_a.id] = [t_a, l_m*math.exp((t_s-0.5)/2)*math.exp((score-2.5)/3)]

    res = []
    for k, v in zip(recommend_activity_dict.keys(), recommend_activity_dict.values()):
        res.append(v)
    res.sort(key=cmp_to_key(cmp))
    
    return [i[0] for i in res][:50]


def get_type_score(user):
    now = datetime.now()
    td = timedelta(days=100)
    start = now - td
    end = now

    click_record = ClickRecord.objects.filter(click_time__range=(start, end))

    act_ids = click_record.filter(user_id=user.id)\
        .values('activity_id').annotate(act_num = Count('activity')).order_by('-act_num')
    act = []
    for i in act_ids:
        act.append(Activity.objects.get(id=i['activity_id']))  
    act_type = [i.activity_type_id for i in act]
    res = dict(Counter(act_type))
    l = len(act_type)
    score = {}
    for k, v in zip(res.keys(), res.values()):
        score[k] = v / l
    return score



def calc_sim(u1, u2):
    ################# 
    ######### 参加活动
    ### 根据活动
    act_1 = u1.attend_activities.all()
    act_2 = u2.attend_activities.all()
    l1 = len(act_1)
    l2 = len(act_2)

    un = set(act_1).union(set(act_2))
    lu = len(un)

    inter = set(act_1).intersection(set(act_2))
    li = len(inter)
    try:
        s_attend_1 = li / lu
    except ZeroDivisionError:
        s_attend_1 = 1

    ###根据类别
    act_1_type = [i.activity_type_id for i in act_1]
    act_2_type = [i.activity_type_id for i in act_2]   
    
    un = set(act_1_type).union(set(act_2_type))
    lu = len(un)

    inter = set(act_1_type).intersection(set(act_2_type))
    li = len(inter)
    try:
        s_attend_2 = li / lu
    except ZeroDivisionError:
        s_attend_2 = 1

    s_attend = s_attend_2 * 0.7 + s_attend_1 * 0.3

    ################# 
    ######### 查看活动
    now = datetime.now()
    td = timedelta(days=100)
    start = now - td
    end = now

    click_record = ClickRecord.objects.filter(click_time__range=(start, end))

    ### 根据活动
    act_u_1 = click_record.filter(user_id=u1.id)\
        .values('activity_id').annotate(act_num = Count('activity')).order_by('-act_num')[:50]

    act_1 = []
    for i in act_u_1:
        act_1.append(Activity.objects.get(id=i['activity_id']))    

    act_u_2 = click_record.filter(user_id=u2.id)\
        .values('activity_id').annotate(act_num = Count('activity')).order_by('-act_num')[:50]

    act_2 = []
    for i in act_u_2:
        act_1.append(Activity.objects.get(id=i['activity_id']))  

    l1 = len(act_1)
    l2 = len(act_2)

    un = set(act_1).union(set(act_2))
    lu = len(un)

    inter = set(act_1).intersection(set(act_2))
    li = len(inter)

    try:
        s_click_1 = li / lu
    except ZeroDivisionError:
        s_click_1 = 1

    act_1_type = [i.activity_type_id for i in act_1]
    act_2_type = [i.activity_type_id for i in act_2]   
    
    un = set(act_1_type).union(set(act_2_type))
    lu = len(un)

    inter = set(act_1_type).intersection(set(act_2_type))
    li = len(inter)

    try:
        s_click_2 = li / lu
    except ZeroDivisionError:
        s_click_2 = 1

    s_click = s_click_2 * 0.7 + s_click_1 * 0.3

    return s_click * 0.3 +  s_attend * 0.7