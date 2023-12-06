from django.db.models import Count

from ars.models import *

from datetime import *
from functools import cmp_to_key
from collections import Counter
import math


def cmp(x, y):
    return y[1] - x[1]


def recommend_commission(user):
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

    finish_commission_list = user.finish_commissions.all()
    type_score = get_type_score(user)

    recommend_commission_dict = {}

    for sim_user, ss in sim_users:
        sim_commission_list = sim_user.finish_commissions.all()
        for com in sim_commission_list:
            if com in finish_commission_list:
                continue
            type_s = 0.
            if com.commission_type.id in type_score:
                type_s = type_score[com.commission_type.id]
            # now_ = now.replace(tzinfo=pytz.timezone('UTC'))
            if com.start_time >= now:
                if com.id not in recommend_commission_dict:
                    recommend_commission_dict[com.id] = [com, sim[sim_user.id] * math.exp((type_s - 0.5) / 5)]

    try:
        l_m = sum([i[1] for i in recommend_commission_dict.values()]) / len(recommend_commission_dict.keys())
    except ZeroDivisionError:
        l_m = 1

    for type_id in type_score.keys():
        commission_type = CommissionType.objects.get(id=type_id)
        type_commissions = commission_type.type_commissions.filter(audit=1)
        t_s = type_score[type_id]
        for idx, t_c in enumerate(type_commissions):
            score = 2.5
            # now_ = now.replace(tzinfo=pytz.timezone('UTC'))
            if t_c.start_time >= now:
                if t_c.id not in recommend_commission_dict:
                    recommend_commission_dict[t_c.id] = [t_c,
                                                         l_m * math.exp((t_s - 0.5) / 2) * math.exp((score - 2.5) / 3)]

    res = []
    for k, v in zip(recommend_commission_dict.keys(), recommend_commission_dict.values()):
        res.append(v)
    res.sort(key=cmp_to_key(cmp))

    return [i[0] for i in res][:50]


def get_type_score(user):
    now = datetime.now()
    td = timedelta(days=100)
    start = now - td
    end = now

    click_record = ClickRecord_Commission.objects.filter(click_time__range=(start, end))

    com_ids = click_record.filter(user_id=user.id) \
        .values('commission_id').annotate(com_num=Count('commission')).order_by('-com_num')
    com = []
    for i in com_ids:
        com.append(Activity.objects.get(id=i['commission_id']))
    com_type = [i.commission_type_id for i in com]
    res = dict(Counter(com_type))
    l = len(com_type)
    score = {}
    for k, v in zip(res.keys(), res.values()):
        score[k] = v / l
    return score


def calc_sim(u1, u2):
    ################# 
    ######### 完成委托
    ### 根据委托
    com_1 = u1.finish_commissions.all()
    com_2 = u2.finish_commissions.all()
    l1 = len(com_1)
    l2 = len(com_2)

    un = set(com_1).union(set(com_2))
    lu = len(un)

    inter = set(com_1).intersection(set(com_2))
    li = len(inter)
    try:
        s_finish_1 = li / lu
    except ZeroDivisionError:
        s_finish_1 = 1

    ###根据类别
    com_1_type = [i.commission_type_id for i in com_1]
    com_2_type = [i.commission_type_id for i in com_2]

    un = set(com_1_type).union(set(com_2_type))
    lu = len(un)

    inter = set(com_1_type).intersection(set(com_2_type))
    li = len(inter)
    try:
        s_finish_2 = li / lu
    except ZeroDivisionError:
        s_finish_2 = 1

    s_finish = s_finish_2 * 0.7 + s_finish_1 * 0.3

    ################# 
    ######### 查看委托
    now = datetime.now()
    td = timedelta(days=100)
    start = now - td
    end = now

    click_record = ClickRecord_Commission.objects.filter(click_time__range=(start, end))

    ### 根据委托
    com_u_1 = click_record.filter(user_id=u1.id) \
                  .values('commission_id').annotate(com_num=Count('commission')).order_by('-com_num')[:50]

    com_1 = []
    for i in com_u_1:
        com_1.append(Commission.objects.get(id=i['commission_id']))

    com_u_2 = click_record.filter(user_id=u2.id) \
                  .values('commission_id').annotate(com_num=Count('commission')).order_by('-com_num')[:50]

    com_2 = []
    for i in com_u_2:
        com_2.append(Commission.objects.get(id=i['commission_id']))

    l1 = len(com_1)
    l2 = len(com_2)

    un = set(com_1).union(set(com_2))
    lu = len(un)

    inter = set(com_1).intersection(set(com_2))
    li = len(inter)

    try:
        s_click_1 = li / lu
    except ZeroDivisionError:
        s_click_1 = 1

    com_1_type = [i.commission_type_id for i in com_1]
    com_2_type = [i.commission_type_id for i in com_2]

    un = set(com_1_type).union(set(com_2_type))
    lu = len(un)

    inter = set(com_1_type).intersection(set(com_2_type))
    li = len(inter)

    try:
        s_click_2 = li / lu
    except ZeroDivisionError:
        s_click_2 = 1

    s_click = s_click_2 * 0.7 + s_click_1 * 0.3

    return s_click * 0.3 + s_finish * 0.7
