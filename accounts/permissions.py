from rest_framework import permissions
from .enums import RoleChoices

class IsAdminOrManagerCanAddEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        requested_role = request.data.get('role')

        if user.role == RoleChoices.ADMIN:
            return True
        elif user.role == RoleChoices.MANAGER:
            return requested_role == RoleChoices.EMPLOYEE
        return False

class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [RoleChoices.ADMIN, RoleChoices.MANAGER]