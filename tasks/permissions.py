from rest_framework.permissions import BasePermission

class RolePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        role = request.user.role
        if role == 'admin':
            return True
        if role == 'manager':
            return view.action in ['list', 'create', 'retrieve','update','partial_update']
        if role == 'employee':
            return view.action in ['list', 'retrieve','partial_update']
        
        return False
    
    def has_object_permission(self, request, view, obj):
        role = request.user.role
        user = request.user
        
        if role == 'admin':
            return True
        if role == 'manager':
            return obj.created_by == user
        if role == 'employee':
            return obj.assigned_to == user
        
        return False