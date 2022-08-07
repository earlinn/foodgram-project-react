from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Allows only the author to edit the recipe."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and obj.author == request.user
        )
