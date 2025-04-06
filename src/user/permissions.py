from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    """
    Allows read-only access to authenticated users, full access to admins.
    """

    def has_permission(self, request, view):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Allows access to the object owner or an admin user.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_superuser
