from django.db.models import Count
from rest_framework import filters
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView

from mapping.models import (
    MappingRule,
    MappingTask,
    MappingEclPart,
    MappingEclPartExclusion,
    MappingECLConcept,
)
from mapping.permissions import (
    MappingProjectAccessPermission,
    MappingTaskAccessPermission,
)
from mapping.serializers import (
    MappingRuleSerializer,
    MappingECLPartSerializer,
    MappingECLConceptSerializer,
    MappingECLConceptExclusionSerializer,
)


class TaskRelatedView:
    permission_classes = [
        MappingProjectAccessPermission,
        MappingTaskAccessPermission,
    ]


class MappingTaskTargetsView(TaskRelatedView, ListCreateAPIView):
    """List and create mapping targets (MappingRules)."""

    serializer_class = MappingRuleSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = [
        "source_component__component_id",
        "source_component__component_title",
        "mapcorrelation",
    ]

    def get_queryset(self):
        task = MappingTask.objects.get(pk=self.kwargs["task_pk"])

        return (
            MappingRule.objects.filter(
                project_id=task.project_id,
                # target_component=task.source_component,
            )
            .select_related(
                "source_component",
                "source_component__codesystem_id",
                "target_component",
                "target_component__codesystem_id",
            )
            .order_by("mapgroup", "mappriority")
        )


class MappingTaskExclusionsView(TaskRelatedView, ListAPIView):
    """List MappingTask exclusions."""

    serializer_class = MappingECLConceptExclusionSerializer

    def get_queryset(self):
        try:
            exclusion = MappingEclPartExclusion.objects.select_related("task").get(
                task_id=self.kwargs["task_pk"]
            )
        except MappingEclPartExclusion.DoesNotExist:
            return MappingECLConcept.objects.none()

        # Filter empty and incorrect components.
        components = [c for c in exclusion.components if c]

        queryset = MappingECLConcept.objects.filter(
            task__project_id=exclusion.task.project_id_id,
            task__source_component__component_id__in=list(components),
        ).select_related("task", "task__source_component")
        return queryset


class MappingTaskECLPartsView(TaskRelatedView, ListAPIView):
    """List ECL Parts for given task."""

    serializer_class = MappingECLPartSerializer

    def get_queryset(self):
        return (
            MappingEclPart.objects.filter(task_id=self.kwargs["task_pk"])
            .annotate(concepts_count=Count("concepts"))
            .order_by("id")
        )


class MappingECLConceptsView(TaskRelatedView, ListAPIView):
    """List All results for a given MappingECLPart."""

    serializer_class = MappingECLConceptSerializer

    def get_queryset(self):
        return MappingECLConcept.objects.filter(
            task_id=self.kwargs["task_pk"]
        ).select_related("ecl")
