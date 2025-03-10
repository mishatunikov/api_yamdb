from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrSuperuser(BasePermission):
    """
    Предоставляет доступ только суперпользователям и пользователям с ролью admin
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.role == 'admin'
        )


class IsAdminOrReadOnly(IsAdminOrSuperuser):
    def has_permission(self, request, view):
        return (super().has_permission(request, view)
                or request.method in SAFE_METHODS
                )
