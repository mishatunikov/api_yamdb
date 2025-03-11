from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrSuperuser(BasePermission):
    """
    Предоставляет доступ только суперпользователям и пользователям с ролью admin
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.role == 'admin'
        )


class IsAdminOrReadOnly(IsAdminOrSuperuser):
    """
    Для аутентифицированных пользователей имеющих статус администратора иначе
    только просмотр.
    """

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            or request.method in SAFE_METHODS
        )


class IsAdminOrOwnerOrReadOnly(BasePermission):
    """
    Для аутентифицированных пользователей имеющих статус администратора или
    автора иначе только просмотр.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.role == 'admin'
            or request.user.role == 'moderator'
            or obj.author == request.user
        )
