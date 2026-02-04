from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users to view/edit their own memberships.
    Admins can view/edit all memberships.
    """

    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Users can only access their own memberships
        return obj.user == request.user


class IsAuthenticatedClient(permissions.BasePermission):
    """
    Permission for regular authenticated users (not admin-only actions)
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
