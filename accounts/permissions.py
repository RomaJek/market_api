
from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        if not request.user:
            return False
        if not request.user.is_authenticated:
            return False
        return True
    


