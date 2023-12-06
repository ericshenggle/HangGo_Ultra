import json

import requests
from django.core.mail import send_mail

from ars.utils import change_data_time_format, change_data_time_format_str, get_access_token


def send_user_in_audit(user):
    access_token = get_access_token()
    payload = {"touser": user.openid, "template_id": "N0g3qePR6hz8Fn79lM_5sIT9jhUTKEYQW5Y_VObffZ0",
               "page": "pages/activity/home/home",
               "miniprogram_state": "trial", "data": {
            "thing7": {
                "value": "新用户注册申请"
            },
            "phrase4": {
                "value": "审核中"
            },
            "thing5": {
                "value": "请关注后续审核状态通知"
            }
        }}
    res = requests.post(url=f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                        json=payload)


def send_user_audit_success(user):
    access_token = get_access_token()
    payload = {"touser": user.openid, "template_id": "mEFV6psbMGpP9i8CU8NXTCVLUApFp2bh8lcP-cJDvj0",
               "page": "pages/activity/home/home",
               "miniprogram_state": "trial", "data": {
            "phrase1": {
                "value": "审核通过"
            },
            "thing5": {
                "value": "恭喜，您的注册申请已经通过!快来体验吧！"
            }
        }}
    res = requests.post(url=f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                        json=payload)


def send_user_audit_fail(user):
    access_token = get_access_token()
    payload = {"touser": user.openid, "template_id": "C4V9ycGzS0BGvjVsmcondcBwFMOvLFQ3sE8j0KKTF0g",
               "page": "pages/activity/home/home",
               "miniprogram_state": "trial", "data": {
            "thing9": {
                "value": "新用户注册"
            },
            "phrase5": {
                "value": "审核失败"
            },
            "thing12": {
                "value": f"抱歉，您的注册已被拒绝，拒绝理由请见邮件"
            }
        }}
    res = requests.post(url=f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                        json=payload)


def send_new_activity_can_select(activity):
    access_token = get_access_token()
    subscribe_users = activity.activity_type.subscribe_users.all()
    followers = activity.create_user.followees.all()
    user_all = subscribe_users | followers
    for user in user_all:
        payload = {"touser": user.openid, "template_id": "ueT_F8NdhXtY9Yh2_3e1mHTdbmtXnZ-PZOmVB_pyTz8",
                   "page": "pages/activity/home/home",
                   "miniprogram_state": "trial", "data": {
                "thing1": {
                    "value": "您的订阅类别或关注的用户有新活动发布！"
                },
                "thing2": {
                    "value": f"活动名称:{activity.name[0:15]}"
                },
                "thing3": {
                    "value": "点击查看详情"
                }
            }}
        res = requests.post(url=f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                            json=payload)


def send_comment_deleted(user, activity):
    access_token = get_access_token()
    payload = {"touser": user.openid, "template_id": "ueT_F8NdhXtY9Yh2_3e1mHTdbmtXnZ-PZOmVB_pyTz8",
               "page": "pages/activity/home/home",
               "miniprogram_state": "trial", "data": {
            "thing1": {
                "value": "您的评论已被管理员删除"
            },
            "thing2": {
                "value": f"活动名称:{activity.name[0:15]}"
            },
            "thing3": {
                "value": "点击查看详情"
            }
        }}
    res = requests.post(url=f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                        json=payload)


def send_activity_in_audit(activity):
    access_token = get_access_token()
    payload = {"touser": activity.create_user.openid, "template_id": "N0g3qePR6hz8Fn79lM_5sIT9jhUTKEYQW5Y_VObffZ0",
               "page": "pages/activity/home/home",
               "miniprogram_state": "trial", "data": {
            "thing7": {
                "value": f"活动创建:{activity.name[0:15]}"
            },
            "phrase4": {
                "value": "活动审核中"
            },
            "thing5": {
                "value": "请关注后续审核状态通知"
            }
        }}
    res = requests.post(url=f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                        json=payload)


def send_activity_audit_pass(activity):
    access_token = get_access_token()
    user = activity.create_user
    payload = {"touser": user.openid, "template_id": "mEFV6psbMGpP9i8CU8NXTJ27dOoppg8FZsYQmN9lHcs",
               "page": "pages/activity/home/home",
               "miniprogram_state": "trial", "data": {
            "thing2": {
                "value": f"活动创建:{activity.name[0:15]}"
            },
            "phrase1": {
                "value": '审核通过'
            },
            "thing5": {
                "value": '您的活动已经审核通过，快邀请别人参加吧'
            }
        }}
    res = requests.post(url=f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                        json=payload)


def send_activity_audit_reject(activity):
    access_token = get_access_token()
    user = activity.create_user
    payload = {"touser": user.openid, "template_id": "C4V9ycGzS0BGvjVsmcondcBwFMOvLFQ3sE8j0KKTF0g",
               "page": "pages/activity/home/home",
               "miniprogram_state": "trial", "data": {
            "thing9": {
                "value": f"活动创建:{activity.name[0:15]}"
            },
            "phrase5": {
                "value": '审核失败'
            },
            "thing12": {
                "value": '您的活动被管理员审核失败，理由请见邮件。'
            }
        }}
    res = requests.post(url=f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                        json=payload)

def send_topic_in_audit(top):
    access_token = get_access_token()
    payload = {"touser": top.create_user.openid, "template_id": "N0g3qePR6hz8Fn79lM_5sIT9jhUTKEYQW5Y_VObffZ0",
               "page": "pages/activity/home/home",
               "miniprogram_state": "trial", "data": {
            "thing7": {
                "value": f"话题创建:{top.name[0:15]}"
            },
            "phrase4": {
                "value": "话题审核通过"
            },
            "thing5": {
                "value": "请关注后续审核状态通知"
            }
        }}
    res = requests.post(url=f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                        json=payload)


def send_Chat_to_user(message):
    access_token = get_access_token()
    payload = {"touser": message.to_user.openid, "template_id": "tnmAvtNzq1q0BHU-eou3pUurmiaRGGpFQxHW9VO5GB4",
               "page": "pages/aboutme/message/message",
               "miniprogram_state": "trial", "data": {
            "name1": {
                "value": f"{message.from_user.nickName}"
            },
            "time3": {
                "value": f"{change_data_time_format_str(message.created_time)}"
            },
            "thing2": {
                "value": f"{message.content}"
            }
        }}
    res = requests.post(url=f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                        json=payload)

def send_Notification_to_user(notification):
    access_token = get_access_token()
    payload = {"touser": notification.user.openid, "template_id": "tnmAvtNzq1q0BHU-eou3pUurmiaRGGpFQxHW9VO5GB4",
               "page": "pages/aboutme/message/message",
               "miniprogram_state": "trial", "data": {
            "name1": {
                "value": "系统通知"
            },
            "time3": {
                "value": f"{change_data_time_format_str(notification.created_time)}"
            },
            "thing2": {
                "value": f"{notification.content}"
            }
        }}
    res = requests.post(url=f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                        json=payload)