import json
import logging

from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from app.serializers import UserSerializer
from mapping.enums import MappingGroups
from mapping.forms import TaskUserForm
from mapping.models import (
    MappingCodesystemComponent,
    MappingEventLog,
    MappingProject,
    MappingRule,
)
from mapping.permissions import MappingProjectAccessPermission

logger = logging.getLogger(__name__)


class MappingProjectUsers(ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [MappingProjectAccessPermission]

    def get_queryset(self):
        logger.info(
            f"[users/MappingUsers retrieve] requested by {self.request.user} - {self.kwargs['project_pk']}"
        )

        return (
            User.objects.filter(groups__name=MappingGroups.project_access)
            .filter(
                Q(tasks__project_id=self.kwargs["project_pk"])
                | Q(access_users__pk=self.kwargs["project_pk"])
            )
            .distinct()
        )

    def create(self, request, project_pk):
        logger.info(
            f"[users/MappingUsers create] requested by {request.user} - data: {str(request.data)[:500]}"
        )

        project = MappingProject.objects.get(pk=project_pk)
        form = TaskUserForm(request.data, project=project)
        if not form.is_valid():
            return Response(
                data={"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        task = form.cleaned_data["task"]
        new_user = form.cleaned_data["user"]

        if task.user == None:
            source_user = User.objects.get(id=1)
        else:
            source_user = task.user

        task.user = new_user
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
        # print(str(mappingrules))
        event = MappingEventLog.objects.create(
            task=task,
            action="user_change",
            action_user=request.user,
            action_description="Gebruiker:",
            old_data="",
            new_data=json.dumps(mappingrules),
            old=str(source_user),
            new=str(new_user),
            user_source=source_user,
            user_target=new_user,
        )
        event.save()

        # Disabled due to resource management -> usual workflow changes user+status, triggering 2 simultaneous audits.
        # audit_async.delay('multiple_mapping', task.project_id.id, task.id)

        return Response([])
