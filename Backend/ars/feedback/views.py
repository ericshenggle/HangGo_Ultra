from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ars.feedback.serializers import FeedBackSerializer
from ars.models import FeedBack


class FeedBackViewSet(viewsets.ModelViewSet):
    queryset = FeedBack.objects.all()
    serializer_class = FeedBackSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(methods=['post'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def user_create_feedback(self, request):
        feed_back = FeedBack(user=request.user, content=request.data.get('content', ''))
        feed_back.save()
        return Response(status=status.HTTP_201_CREATED)
