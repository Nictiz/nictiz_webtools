from rest_framework import permissions, viewsets
from rest_framework.response import Response


class Permission_MappingProject_Access(permissions.BasePermission):
    """
    Global permission check rights to use the RC Audit functionality.
    """

    def has_permission(self, request, view):
        if "mapping | access" in request.user.groups.values_list("name", flat=True):
            return True


class Permission_MappingProject_Whitelist(permissions.BasePermission):
    """
    Global permission check rights to use the whitelist functionality.
    """

    def has_permission(self, request, view):
        if "mapping | audit whitelist" in request.user.groups.values_list(
            "name", flat=True
        ):
            return True


class SnomedFailbackImport(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_Whitelist]

    """
    Will import SNOMED concepts in ECL query: '<<pk'
    """

    def retrieve(self, request, pk=None):
        print(
            f"[snomed_failback_import/SnomedFailbackImport retrieve] requested by {request.user} - {pk}"
        )

        conceptid = str(pk)
        # import_snomed_async(conceptid)

        return Response(f"Started import [{str(pk)}]")
