from rest_framework.permissions import BasePermission

class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Moderators').exists()

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsNotModerator(BasePermission):
    """Пользователь аутентифицирован и НЕ является модератором."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.groups.filter(name='Moderators').exists()

class IsModeratorOrOwner(BasePermission):
    """Пользователь – модератор ИЛИ владелец объекта."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.groups.filter(name='Moderators').exists():
            return True

        return obj.owner == user