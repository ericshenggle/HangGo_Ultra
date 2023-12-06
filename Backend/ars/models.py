from django.contrib.auth.models import AbstractUser
from django.db import models


class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    verify_code = models.TextField(null=True)


class User(AbstractUser):
    class GenderChoice(models.IntegerChoices):
        未知 = 0
        男 = 1
        女 = 2

    class AuditStatus(models.IntegerChoices):
        待审核 = 1
        审核中 = 2
        已通过 = 3

    nickName = models.CharField(max_length=255, verbose_name='昵称')
    avatarUrl = models.CharField(max_length=255, verbose_name='头像地址')
    openid = models.CharField(max_length=255, unique=True, verbose_name='openid')
    age = models.IntegerField(null=True)
    gender = models.IntegerField(choices=GenderChoice.choices)
    student_id = models.CharField(max_length=255)  # 研究生的学号带有字母
    phone = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    audit_status = models.IntegerField(choices=GenderChoice.choices, default=AuditStatus.待审核)
    credential = models.ImageField(null=True, verbose_name='上传证明')
    sso_password = models.CharField(max_length=255, null=True)
    bykc_isactive = models.BooleanField(default=False)
    authority = models.CharField(max_length=10, default="1111")
    followers = models.ManyToManyField('self', null=True, related_name='followees', verbose_name='关注的用户',
                                       symmetrical=False)    


class ActivityType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='activityType', null=True)
    subscribe_users = models.ManyToManyField(User, through='Subscribe', related_name='subscribe_activity_types')


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Activity(models.Model):
    class LocationChoice(models.IntegerChoices):
        学院路 = 1
        沙河 = 2
        校外 = 3

    class PublicStatusChoice(models.IntegerChoices):
        草稿 = 1
        已提交审核 = 2
        已发布 = 3

    class AuditStatusChoice(models.IntegerChoices):
        未审核 = 1
        审核中 = 2
        审核通过 = 3
        审核失败 = 4

    name = models.CharField(max_length=255)
    activity_type = models.ForeignKey(ActivityType, related_name='type_activities', on_delete=models.PROTECT)
    start_enrollment_at = models.DateTimeField()
    end_enrollment_at = models.DateTimeField()
    create_user = models.ForeignKey(User, related_name='create_activities', on_delete=models.PROTECT)
    location = models.IntegerField(choices=LocationChoice.choices)
    latitude = models.FloatField(null=True)  # for sports
    longitude = models.FloatField(null=True)  # for sports
    position = models.TextField()
    public_status = models.IntegerField(choices=PublicStatusChoice.choices)
    photo = models.ImageField(null=True, upload_to='act/')
    audit_status = models.IntegerField(choices=AuditStatusChoice.choices)
    attend_users = models.ManyToManyField(User, through='UserActivity', related_name='attend_activities')
    tags = models.ManyToManyField(Tag, related_name='tag_activities')
    click_users = models.ManyToManyField(User, through='ClickRecord', related_name='click_activities')
    bykc_id = models.IntegerField(null=True, db_index=True)
    bykc_has_attend_number = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class ActivityInfo(models.Model):  # 除了教务课程以外的所有活动
    activity = models.ForeignKey(Activity, related_name='normal_activity', on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    description = models.TextField()
    allow_total = models.IntegerField()


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    remark = models.IntegerField(null=True)


class Comment(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_comment', on_delete=models.CASCADE)
    comment = models.TextField()
    comment_time = models.DateTimeField(null=True, auto_now_add=True)
    at_user = models.ForeignKey(User, null=True, related_name='user_at', on_delete=models.CASCADE)


class Keyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.TextField()
    search_time = models.DateTimeField(null=True, auto_now_add=True)


class ClickRecord(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    click_time = models.DateTimeField(null=True, auto_now_add=True)


class Subscribe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.ForeignKey(ActivityType, on_delete=models.CASCADE)


class ActivityPhoto(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='pictures')
    photo = models.ImageField()


class TalkMessage(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(null=False)
    is_read = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)


class FeedBack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_backs')
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)


class CommissionType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='commissionType', null=True)


class Commission(models.Model):
    class LocationChoice(models.IntegerChoices):
        学院路 = 1
        沙河 = 2

    class RealTimeChoice(models.IntegerChoices):
        实时 = 1
        非实时 = 2

    class PublicStatusChoice(models.IntegerChoices):
        已发布 = 1
        已申请 = 2
        已完成 = 3
        已评分 = 4

    class AuditStatusChoice(models.IntegerChoices):
        审核通过 = 1
        审核失败 = 2

    name = models.CharField(max_length=255)
    commission_type = models.ForeignKey(CommissionType, related_name='type_commissions', on_delete=models.PROTECT)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    real_time = models.IntegerField(choices=RealTimeChoice.choices)
    user = models.ForeignKey(User, related_name='create_commissions', on_delete=models.PROTECT)
    location = models.IntegerField(choices=LocationChoice.choices)
    status = models.IntegerField(choices=PublicStatusChoice.choices)
    description = models.TextField()
    audit = models.IntegerField(choices=AuditStatusChoice.choices)
    fee = models.IntegerField()
    user_accept = models.ForeignKey(User, related_name='accept_commissions', on_delete=models.PROTECT, null=True)

    click_users = models.ManyToManyField(User, through='ClickRecord_Commission', related_name='click_commissions')
    tags = models.ManyToManyField(Tag, through='Commission_Tags', related_name='tag_commissions')

    def __str__(self):
        return self.name


class Commission_Accept(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE)
    apply_time = models.DateTimeField(null=True, auto_now_add=True)


class Commission_Comment(models.Model):
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_commission_comment', on_delete=models.CASCADE)
    comment = models.TextField()
    comment_time = models.DateTimeField(null=True, auto_now_add=True)

class Commission_Comment_Reply(models.Model):
    to_comment = models.ForeignKey(Commission_Comment, related_name='user_commission_reply_at', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, null=True, related_name='user_commission_reply_user_at', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_commission_reply', on_delete=models.CASCADE)
    comment = models.TextField()
    comment_time = models.DateTimeField(null=True, auto_now_add=True)


class UserCommission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='finish_commissions')
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE)
    score = models.IntegerField(null=True)

class Commission_Tags(models.Model):
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

class ClickRecord_Commission(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE)
    click_time = models.DateTimeField(null=True, auto_now_add=True)


class SearchRecord_Commission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.TextField()
    search_time = models.DateTimeField(null=True, auto_now_add=True)


class TopicType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='topicType/', null=True)


class Topic(models.Model):
    class AuditStatusChoice(models.IntegerChoices):
        审核通过 = 1
        审核失败 = 2

    name = models.CharField(max_length=255)
    topic_type = models.ForeignKey(TopicType, related_name='type_topics', on_delete=models.PROTECT)
    create_at = models.DateTimeField()
    create_user = models.ForeignKey(User, related_name='create_topics', on_delete=models.PROTECT)
    description = models.TextField()
    audit = models.IntegerField(choices=AuditStatusChoice.choices)
    photos = models.ImageField(upload_to='topic/', null=True)

    click_users = models.ManyToManyField(User, through='ClickRecord_Topic', related_name='click_topics')
    tags = models.ManyToManyField(Tag, related_name='tag_topics')

    def __str__(self):
        return self.name

class TopicInfo(models.Model):  # 除了教务课程以外的所有活动
    topic = models.ForeignKey(Topic, related_name='normal_topic', on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    description = models.TextField()

class Topic_Comment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_topic_comment', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user_topic_comment', on_delete=models.CASCADE)
    comment_content = models.TextField()
    comment_time = models.DateTimeField(null=True, auto_now_add=True)


class UserTopic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


class ClickRecord_Topic(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    click_time = models.DateTimeField(null=True, auto_now_add=True)


class SearchRecord_Topic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.TextField()


class Topic_Subscribe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, related_name= 'sub_topic',  on_delete=models.CASCADE)

class Topic_Like(models.Model):
    user = models.ForeignKey(User, related_name= 'liked_user', on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, related_name= 'liked_topic', on_delete=models.CASCADE)

class Topic_Comment_Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic_comment = models.ForeignKey(Topic_Comment, related_name= 'liked_topic_comment', on_delete=models.CASCADE)

class Topic_Notification(models.Model):
    class Topic_NotificationType(models.IntegerChoices):
        话题回复 = 1
        话题内评论回复 = 2
        系统通知 = 3

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    type = models.IntegerField(choices=Topic_NotificationType.choices)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    isread = models.BooleanField(default=False)

class Topic_Keyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.TextField()
    search_time = models.DateTimeField(null=True, auto_now_add=True)

class Notification(models.Model):
    class NotificationType(models.IntegerChoices):
        日程提醒 = 1
        系统通知 = 2
        活动推荐 = 3
        订阅提醒 = 4
        评论回复 = 5
        委托评分 = 6

    class Type(models.IntegerChoices):
        活动 = 1
        委托 = 2
        话题 = 3
        权限 = 4

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    not_type = models.IntegerField(choices=NotificationType.choices)
    type = models.IntegerField(choices=Type.choices)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True)
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    isread = models.BooleanField(default=False)


class Appeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    authority = models.IntegerField()
    reason = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    isSave = models.BooleanField(default=False)


class Inform(models.Model):
    user = models.ForeignKey(User, related_name='user_inform', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user_inform', on_delete=models.CASCADE)
    authority = models.IntegerField()
    reason = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    isSave = models.BooleanField(default=False)