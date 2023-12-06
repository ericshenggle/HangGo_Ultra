from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = '平行权限验证失败'
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class IsOwner(permissions.BasePermission):
    message = '平行权限验证失败'

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsUser(permissions.BasePermission):
    message = '平行权限验证失败'

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsUserOrReadOnly(permissions.BasePermission):
    message = '平行权限验证失败'
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user


# 针对User模型本身做验证
class IsSelfUser(permissions.BasePermission):
    message = '平行权限验证失败'
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id
