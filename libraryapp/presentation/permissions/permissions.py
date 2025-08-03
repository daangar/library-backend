from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and
            request.user.groups.filter(name='Students').exists()
        )


class IsLibrarian(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and
            request.user.groups.filter(name='Librarians').exists()
        )


class IsOwnerOrLibrarian(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='Librarians').exists():
            return True
        
        if hasattr(obj, 'student'):
            return obj.student.id == request.user.id
        
        return False