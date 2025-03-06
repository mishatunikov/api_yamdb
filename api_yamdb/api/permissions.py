from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin)


class IsAdminOrReadOnly(AdminOnly):
    def has_permission(self, request, view):
        return (super().has_permission(request, view)
                or request.method in permissions.SAFE_METHODS
                )
