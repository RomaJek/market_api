
from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        if not request.user:
            return False
        if not request.user.is_authenticated:
            return False
        return True
    

class IsAdminOrSuperAdmin(BasePermission):
    """ Tek admin ham superadmin ushin ruxsat """
    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role in [request.user.ADMIN, request.user.SUPER_ADMIN]:
            return True

        return False

