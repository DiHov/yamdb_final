from rest_framework import permissions

from yamdb.models import Role


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = getattr(request.user, "role", None)
        return user_role == Role.ADMIN or request.user.is_superuser


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = getattr(request.user, "role", None)
        return user_role == Role.MODERATOR


class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class ReviewAndCommentPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.role == Role.ADMIN
                or request.user.role == Role.MODERATOR)
