from rest_framework import permissions


class IsSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user.is_superuser


class IsAdminOrIsSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_superuser


class IsSelfOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id


class IsReadOnly(permissions.BasePermission):
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
