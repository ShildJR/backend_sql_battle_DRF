from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Разрешение для администраторов"""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsParticipant(BasePermission):
    """Разрешение для участников"""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'participant'
        )
