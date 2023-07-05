from rest_framework import permissions


class Permission_MappingTaskEditor_Access(permissions.BasePermission):
    """
    Global permission check rights to use the RC Audit functionality.
    """

    def has_permission(self, request, view):
        if "mapping | view tasks" in request.user.groups.values_list("name", flat=True):
            return True
