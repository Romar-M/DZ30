from rest_framework.permissions import BasePermission

class IsModerator(BasePermission):
    """
    Разрешение для модераторов (состоит в группе Moderators).
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Moderators').exists()

class IsOwner(BasePermission):
    """
    Разрешение на уровне объекта – только владелец.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user