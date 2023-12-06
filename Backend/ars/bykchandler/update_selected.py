import pytz

from ars.models import Activity, ActivityInfo, UserActivity, Notification
from ars.bykchandler import utils
from django.utils import timezone

from ars.notification.wxapi import send_new_activity_can_select


def update_unselected(user):
    if user.sso_password is not None and user.student_id is not None:
        token, session = utils.get_token(user.student_id, user.sso_password)
        res = utils.post_api(session, token, user.student_id, user.sso_password, 'querySelectableCourse', {})
        for item in res:
            try:
                act = Activity.objects.get(bykc_id=item['id'])
                act.bykc_has_attend_number = item['courseCurrentCount']
                act.save()
            except Activity.DoesNotExist:
                act = Activity()
                act.name = item['courseName']
                act.activity_type_id = 9
                act.start_enrollment_at = pytz.timezone('Asia/Shanghai').localize(
                    timezone.datetime.strptime(item['courseSelectStartDate'],
                                               "%Y-%m-%d %H:%M:%S"))
                act.end_enrollment_at = pytz.timezone('Asia/Shanghai').localize(
                    timezone.datetime.strptime(item['courseSelectEndDate'],
                                               "%Y-%m-%d %H:%M:%S"))
                act.create_user_id = 1
                act.location = Activity.LocationChoice.学院路
                act.latitude = None
                act.longitude = None
                act.position = item['coursePosition']
                act.public_status = Activity.PublicStatusChoice.已发布
                act.audit_status = Activity.AuditStatusChoice.审核通过
                act.bykc_id = item['id']
                act.bykc_has_attend_number = item['courseCurrentCount']
                act.save()
                act_info = ActivityInfo()
                act_info.activity = act
                act_info.start_at = pytz.timezone('Asia/Shanghai').localize(
                    timezone.datetime.strptime(item['courseStartDate'],
                                               "%Y-%m-%d %H:%M:%S"))
                act_info.end_at = pytz.timezone('Asia/Shanghai').localize(
                    timezone.datetime.strptime(item['courseEndDate'],
                                               "%Y-%m-%d %H:%M:%S"))
                act_info.description = "博雅课程"
                act_info.allow_total = item['courseMaxCount']
                act_info.save()
                send_new_activity_can_select(act)
                # 实现向用户订阅了博雅的用户推送这个课程
                subscribe_users = act.activity_type.subscribe_users.all()
                for user in subscribe_users:
                    Notification(user=user, not_type=Notification.NotificationType.订阅提醒, type=Notification.Type.活动, isread=False,
                                 activity=act,
                                 content='您订阅的类别' + act.activity_type.name + '有新的活动' + act.name + '！请点击查看').save()
                followers = act.create_user.followers.all()
                for user in followers:
                    Notification(user=user, not_type=Notification.NotificationType.订阅提醒, type=Notification.Type.活动, isread=False,
                                 activity=act,
                                 content='您关注的用户' + act.create_user.username + '有新的活动' + act.name + '发布！请点击查看').save()


def update_selected(user):
    if user.sso_password is not None and user.student_id is not None:
        token, session = utils.get_token(user.student_id, user.sso_password)
        res = utils.post_api(session, token, user.student_id, user.sso_password, 'queryChosenCourse', {})
        id_list = []
        for item in res['courseList']:
            try:
                act = Activity.objects.get(bykc_id=item['courseInfo']['id'])
            except Activity.DoesNotExist:
                act = Activity()
                act.name = item['courseInfo']['courseName']
                act.activity_type_id = 9
                act.start_enrollment_at = pytz.timezone('Asia/Shanghai').localize(
                    timezone.datetime.strptime(item['courseInfo']['courseSelectStartDate'],
                                               "%Y-%m-%d %H:%M:%S"))
                act.end_enrollment_at = pytz.timezone('Asia/Shanghai').localize(
                    timezone.datetime.strptime(item['courseInfo']['courseSelectEndDate'],
                                               "%Y-%m-%d %H:%M:%S"))
                act.create_user_id = 1
                act.location = Activity.LocationChoice.学院路
                act.latitude = None
                act.longitude = None
                act.position = item['courseInfo']['coursePosition']
                act.public_status = Activity.PublicStatusChoice.已发布
                act.audit_status = Activity.AuditStatusChoice.审核通过
                act.bykc_id = item['courseInfo']['id']
                act.bykc_has_attend_number = item['courseInfo']['courseCurrentCount']
                act.save()
                act_info = ActivityInfo()
                act_info.activity = act
                act_info.start_at = pytz.timezone('Asia/Shanghai').localize(
                    timezone.datetime.strptime(item['courseInfo']['courseStartDate'],
                                               "%Y-%m-%d %H:%M:%S"))
                act_info.end_at = pytz.timezone('Asia/Shanghai').localize(
                    timezone.datetime.strptime(item['courseInfo']['courseEndDate'],
                                               "%Y-%m-%d %H:%M:%S"))
                act_info.description = "博雅课程"
                act_info.allow_total = item['courseInfo']['courseMaxCount']
                act_info.save()
            if not user.attend_activities.filter(id=act.id).exists():
                user.attend_activities.add(act)
            id_list.append(act.id)
            # 删除掉已经推选的课程
        removed_selected = UserActivity.objects.filter(user_id=user.id).filter(activity__activity_type_id=9).exclude(
            activity_id__in=id_list)  # 不在列表中的活动
        removed_selected.delete()
        return token, session
    else:
        raise RuntimeError("没有提供账号和密码")
