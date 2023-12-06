from django.db.models import Avg
from rest_framework import serializers
from ars.models import User, Activity, UserActivity, UserCommission


class UserSerializer(serializers.ModelSerializer):
    attend_activities_count = serializers.SerializerMethodField()
    create_activities_count = serializers.SerializerMethodField()
    unread_message_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'nickName', 'avatarUrl', 'email', 'openid', 'age', 'gender', 'student_id', 'phone',
                  'audit_status', 'is_staff', 'credential', 'subscribe_activity_types', 'attend_activities_count',
                  'create_activities_count', 'unread_message_count', 'bykc_isactive', 'authority']
        read_only_fields = ['id', 'audit_status', 'is_staff', 'bykc_isactive']
        code = serializers.CharField()
        depth = 1

        def create(self, validated_data):
            user = User.objects.create_user(validated_data['email'], audit_status=User.AuditStatus.审核中,
                                            is_active=False, **validated_data)
            user.username = user.email
            user.save()
            if user.email.endswith('@buaa.edu.cn'):
                user.is_active = True
                user.audit_status = User.AuditStatus.已通过
                user.save()
            return user

    def get_attend_activities_count(self, obj):
        return obj.attend_activities.count()

    def get_create_activities_count(self, obj):
        return obj.create_activities.filter(audit_status=Activity.AuditStatusChoice.审核通过).count()

    def get_unread_message_count(self, obj):
        return obj.notification_set.filter(isread=False).count()


class UserPublicSerializer(serializers.ModelSerializer):
    is_followed = serializers.SerializerMethodField()
    average_rate = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'nickName', 'avatarUrl', 'email', 'age', 'gender', 'audit_status',
                  'is_staff', 'is_followed', 'average_rate']
        read_only_fields = ['id', 'audit_status', 'is_staff']

    def get_is_followed(self, obj):
        request = self.context.get("request", None)
        if request is None or not request.user.is_authenticated:
            return None
        return request.user.followers.filter(id=obj.id).count() > 0

    def get_average_rate(self, obj):
        dict1 = UserActivity.objects.filter(activity__create_user=obj).aggregate(Avg("remark"))
        dict2 = UserCommission.objects.filter(user=obj).aggregate(Avg("score"))
        return dict(**dict1, **dict2)


class UserSuperAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

class UserAuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickName', 'avatarUrl', 'authority']
