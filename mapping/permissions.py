from django.contrib.auth.models import Group
from rest_framework import permissions

from mapping.enums import MappingGroups
from mapping.models import MappingTask


class MappingAccessPermission(permissions.BasePermission):
    """Check if user has access to `MappingGroups.project_access`."""

    def has_permission(self, request, view):
        return request.user.groups.filter(name=MappingGroups.project_access).exists()


class MappingProjectAccessPermission(MappingAccessPermission):
    """
    Global permission check rights to use the RC Audit functionality.
    """

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        if "project_pk" in view.kwargs:
            return request.user.access_users.filter(pk=view.kwargs["project_pk"]).exists()
        return True
 

class MappingTaskAccessPermission(MappingAccessPermission):
    """Check if user has access to given task."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
    
        if "task_pk" in view.kwargs:
            return MappingTask.objects.filter(
                pk=view.kwargs["task_pk"]
            ).exists()
        return True