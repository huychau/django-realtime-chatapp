from rest_framework import permissions


class IsAdminOrIsSelf(permissions.BasePermission):
    """
    Check user request is admin or self
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_superuser


class IsAdminReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow access to lists, gets for admins
    """

    def has_permission(self, request, view):
        return view.action not in ('list', 'retrieve') or request.user \
            and request.user.is_superuser


class IsAuthenticatedReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow user logged in see list
    """

    def has_permission(self, request, view):
        if view.action in ('list', 'retrieve'):
            # check user is authenticated for 'list' route requests
            return request.user and request.user.is_authenticated
        return True


class IsSelfOrAdminUpdateDeleteOnly(permissions.BasePermission):
    """
    Custom permission:
        - Allow anonymous POST, GET
        - Allow owner or admin can PUT, DELETE
    """

    def has_object_permission(self, request, view, obj):
        if view.action in ('create', 'retrieve', 'me'):
            return True

        return view.action in ['update', 'partial_update', 'destroy'] \
            and obj.id == request.user.id or request.user.is_superuser
