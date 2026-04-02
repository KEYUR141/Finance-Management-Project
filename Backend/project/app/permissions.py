from rest_framework.permissions import BasePermission



class IsAdminOrNot(BasePermission):
    def has_permission(self, request, view):
        try:
            return (
                request.user.is_authenticated and
                request.user.profile.role == 'admin'
            )
        except Exception as e:
            return False

class IsAnalystOrAbove(BasePermission):
    def has_permission(self, request, view):
        try:
            return (
                request.user.is_authenticated and
                request.user.profile.role in ['analyst', 'admin']
            )
        except Exception as e:
            return False
        
class IsViewerOrAbove(BasePermission):
    def has_permission(self, request, view):
        try:
            return (
                request.user.is_authenticated and
                request.user.profile.role in ['viewer', 'analyst', 'admin']
            )
        except Exception as e:
            return False