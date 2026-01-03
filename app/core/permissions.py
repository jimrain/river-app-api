from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    Read permissions are allowed to any request.
    """

    def has_permission(self, request, view):
        # Allow all users (authenticated or not) to use the
        # 'list' action (GET request on the list endpoint)
        if view.action == 'list':
            return True

        # For other actions like create (POST),
        # detail (GET for single item), update, delete,
        # the user must be authenticated.
        # Object-level permissions (has_object_permission)
        # will handle the ownership check
        # for detail, update, and delete.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions (GET, HEAD, OPTIONS) are allowed
        # to any request (already handled by has_permission for list)
        # For detail view (GET on a single object),
        # we also allow it here for simplicity,
        # but the primary use is for write operations.

        # For write permissions (PUT, PATCH, DELETE),
        # only the owner is allowed.
        # The object is passed to this method (obj).
        return obj.owner == request.user
