from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the contact (obj)
        return obj.user == request.user
