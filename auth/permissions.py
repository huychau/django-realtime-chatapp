from rest_framework import permissions


class IsSelf(permissions.BasePermission):
    """
    Check user request the resources he/she is owner
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsAdmin(permissions.BasePermission):
    """
    Check user request is admin
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user.is_superuser


class IsAdminOrIsSelf(permissions.BasePermission):
    """
    Check user request is admin or self
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_superuser


class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Check the owner can read only
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id


class IsReadOnly(permissions.BasePermission):
    """
    Is read only permission
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True


class IsAdminListOnly(permissions.BasePermission):
    """
    Custom permission to only allow access to lists for admins
    """

    def has_permission(self, request, view):
        return view.action != 'list' or request.user \
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
        if view.action in ['create', 'retrieve']:
            return True

        return view.action in ['update', 'partial_update', 'destroy'] \
            and obj.id == request.user.id or request.user.is_superuser
