from rest_framework import routers
import ars.user.views
import ars.notification.views
import ars.audit.views
import ars.activity_photo.views
import ars.feedback.views
from ars import activity, activity_tag, activity_type, views, comment, follow, talk_message, commission, \
    topic_like, topic_comment_like, topic, topic_comment, topic_follow, topic_search, topic_type, topic_click, appealOrInform
from ars.auth import views as ars_views
from ars import select, search
from ars.bykchandler import urls
from django.urls import include, path

router = routers.DefaultRouter()
router.register(r'users', ars.user.views.UserViewSet)
router.register(r'notifications', ars.notification.views.NotificationViewSet)
router.register(r'users_admin', ars.audit.views.AuditUserViewSet)
router.register(r'activity_photos', ars.activity_photo.views.ActivityPhotoViewSet)
router.register(r'feedbacks', ars.feedback.views.FeedBackViewSet)

urlpatterns = [
    path('auth/', ars_views.WxAuthToken.as_view()),
    path('web_auth/', ars_views.WebLogin.as_view()),
    path('', include(router.urls)),
    path('', include(select.urls)),
    path('', include(ars.bykchandler.urls)),
    # path('activities/', include(ars.activity.urls)),

    ###########################################
    # activity related
    path('', include(ars.search.urls)),
    path('', include(ars.activity.urls)),
    path('', include(ars.activity_type.urls)),
    path('', include(ars.activity_tag.urls)),

    path('', include(ars.comment.urls)),
    path('', include(ars.follow.urls)),
    path('', include(ars.talk_message.urls)),

    # commission related
    path('', include(ars.commission.urls)),

    # path('init_db/', views.Init_DB_view.as_view())

    # topic related
    path('', include(ars.topic.urls)),
    path('', include(ars.topic_comment.urls)),
    path('', include(ars.topic_follow.urls)),
    path('', include(ars.topic_search.urls)),
    path('', include(ars.topic_like.urls)),
    path('', include(ars.topic_comment_like.urls)),
    path('', include(ars.topic_search.urls)),
    path('', include(ars.topic_type.urls)),
    path('', include(ars.topic_click.urls)),

    # appealOrInform related
    path('', include(ars.appealOrInform.urls)),
]
