from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return request.method != 'POST'
        return True

    def has_object_permission(self, request, view, obj):
        
        return True