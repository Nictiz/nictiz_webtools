import json

from django.contrib.auth.models import User
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from mapping.models import (
    MappingCodesystemComponent,
    MappingEventLog,
    MappingProject,
    MappingRule,
    MappingTask,
    MappingTaskStatus,
)


class Permission_MappingProject_Access(permissions.BasePermission):
    """
    Global permission check rights to use the RC Audit functionality.
    """

    def has_permission(self, request, view):
        if "mapping | access" in request.user.groups.values_list("name", flat=True):
            return True


class MappingStatuses(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_Access]

    def retrieve(self, request, pk=None):
        print(f"[status/MappingStatuses retrieve] requested by {request.user} - {pk}")

        current_user = User.objects.get(id=request.user.id)
        project = MappingProject.objects.get(id=pk, access__username=current_user)
        status_list = MappingTaskStatus.objects.filter(project_id=project).order_by(
            "status_id"
        )
        output = []
        for status in status_list:
            output.append(
                {
                    # 'project' : status.project_id.id,
                    "title": status.status_title,
                    "text": status.status_title,
                    "status_id": status.status_id,
                    "value": status.id,
                    "id": status.id,
                    "description": status.status_description,
                    "next": status.status_next,
                }
            )

        return Response(output)

    def create(self, request):
        from mapping.tasks.qa_orchestrator import audit_async

        print(
            f"[status/MappingStatuses create] requested by {request.user} - data: {str(request.data)[:500]}"
        )

        task = MappingTask.objects.get(id=request.data.get("task"))
        current_user = User.objects.get(id=request.user.id)
        if (
            "mapping | change task status"
            in request.user.groups.values_list("name", flat=True)
        ) and MappingProject.objects.filter(
            id=task.project_id.id, access__username=current_user
        ).exists():
            current_user = User.objects.get(id=request.user.id)
            new_status = MappingTaskStatus.objects.get(id=request.data.get("status"))
            old_status = task.status.status_title
            old_task = str(task)
            task.status = new_status
            task.save()

            # Save snapshot to database
            source_component = MappingCodesystemComponent.objects.get(
                id=task.source_component.id
            )
            mappingquery = MappingRule.objects.filter(
                source_component_id=source_component.id
            )
            mappingrules = []
            for rule in mappingquery:
                bindings = []
                for binding in rule.mapspecifies.all():
                    bindings.append(binding.id)
                mappingrules.append(
                    {
                        "Rule ID": rule.id,
                        "Project ID": rule.project_id.id,
                        "Project": rule.project_id.title,
                        "Target codesystem": rule.target_component.codesystem_id.codesystem_title,
                        "Target component ID": rule.target_component.component_id,
                        "Target component Term": rule.target_component.component_title,
                        "Mapgroup": rule.mapgroup,
                        "Mappriority": rule.mappriority,
                        "Mapcorrelation": rule.mapcorrelation,
                        "Mapadvice": rule.mapadvice,
                        "Maprule": rule.maprule,
                        "Active": rule.active,
                        "Bindings": bindings,
                    }
                )

            event = MappingEventLog.objects.create(
                task=task,
                action="status_change",
                action_user=current_user,
                action_description="Status:",
                old_data="",
                new_data=json.dumps(mappingrules),
                old=old_status,
                new=task.status.status_title,
                user_source=current_user,
            )
            event.save()
            audit_async.delay("multiple_mapping", task.project_id.id, task.id)

            return Response([])
        else:
            return Response("Geen toegang", status=status.HTTP_401_UNAUTHORIZED)
