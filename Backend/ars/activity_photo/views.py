from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ars.models import ActivityPhoto, Activity
from ars.activity_photo.serializer import ActivityPhotoSerializer


class ActivityPhotoViewSet(viewsets.ModelViewSet):
    queryset = ActivityPhoto.objects.all()
    serializer_class = ActivityPhotoSerializer

    permission_classes = [permissions.IsAdminUser]

    @action(methods=['get'], detail=False, permission_classes=[])
    def get_photos(self, request):
        if 'activity_id' not in request.data:
            return Response(data={'detail': '缺失id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            activity = Activity.objects.get(pk=request.data['activity_id'])
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        objects = activity.pictures.all()
        serializer = ActivityPhotoSerializer(objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def delete_photo(self, request):
        if 'id' not in request.data:
            return Response(data={'detail': '缺失字段'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            activityphoto = ActivityPhoto.objects.get(pk=request.data['id'])
        except ActivityPhoto.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if activityphoto.activity.create_user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        activityphoto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def upload_photo(self, request):
        data = request.data.copy()
        try:
            activity = Activity.objects.get(pk=request.data['activity_id'])
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if activity.create_user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        data['activity'] = activity.id
        serializer = ActivityPhotoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
