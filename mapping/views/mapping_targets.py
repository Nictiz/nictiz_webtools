from django.db.models import Count
from django.shortcuts import get_object_or_404
import django_filters.rest_framework
from rest_framework import filters
from rest_framework.generics import ListAPIView, ListCreateAPIView, UpdateAPIView

from mapping.models import (
    MappingECLConcept,
    MappingEclPart,
    MappingEclPartExclusion,
    MappingProjectAudit,
    MappingRule,
    MappingTask,
)
from mapping.permissions import (
    MappingProjectAccessPermission,
    MappingTaskAccessPermission,
)
from mapping.serializers import (
    MappingECLConceptExclusionSerializer,
    MappingECLConceptSerializer,
    MappingECLPartSerializer,
    MappingProjectAuditSerializer,
    MappingRuleSerializer,
)


class TaskRelatedView:
    permission_classes = [
        MappingProjectAccessPermission,
        MappingTaskAccessPermission,
    ]


class MappingTaskTargetsView(TaskRelatedView, ListCreateAPIView):
    """List and create mapping targets (MappingRules)."""

    serializer_class = MappingRuleSerializer
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend
    ]

    ordering_fields = [
        "source_component__component_id",
        "source_component__component_title",
        "mapcorrelation",
    ]
    filterset_fields = [
        "source_component__component_title",
        "source_component__component_id"
    ]
    search_fields = [
        "^source_component__component_id",
        "^source_component__component_title"
    ]

    def get_queryset(self):
        task = MappingTask.objects.get(pk=self.kwargs["task_pk"])

        return (
            MappingRule.objects.filter(
                project_id=task.project_id,
                target_component=task.source_component,
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
    filter_backends = [
        filters.OrderingFilter,
    ]
    ordering_fields = [
        "task__source_component__component_id",
        "task__source_component__component_title",
        "code",
    ]

    def get_queryset(self):
        task = MappingTask.objects.select_related("source_component").get(pk=self.kwargs["task_pk"])

        exclude_components = [] if task.exclusions is None else task.exclusions

        try:
            remote_exclusion = MappingEclPartExclusion.objects.get(task=task)
        except MappingEclPartExclusion.DoesNotExist:
            pass
        else:
            exclude_components = list(set(exclude_components + remote_exclusion.components))

        task_concepts = MappingECLConcept.objects.filter(
            task=task,
        ).values_list("code", flat=True)

        # Filter empty and incorrect components.
        queryset = MappingECLConcept.objects.filter(
            code__in=task_concepts,
            task__project_id=task.project_id_id,
            task__source_component__codesystem_id_id=task.source_component.codesystem_id_id,
            task__source_component__component_id__in=exclude_components,
        ).select_related("task", "task__source_component")

        return queryset


class MappingTaskECLPartsView(TaskRelatedView, ListCreateAPIView):
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
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]

    filterset_fields = ["code", "ecl_id"]
    search_fields = ["^id", "^code"]

    def get_queryset(self):
        task = MappingTask.objects.select_related("source_component").get(pk=self.kwargs["task_pk"])

        exclude_components = [] if task.exclusions is None else task.exclusions

        try:
            remote_exclusion = MappingEclPartExclusion.objects.get(task=task)
        except MappingEclPartExclusion.DoesNotExist:
            pass
        else:
            exclude_components = list(set(exclude_components + remote_exclusion.components))

        exclusions = MappingECLConcept.objects.filter(
            task__project_id=task.project_id_id,
            task__source_component__codesystem_id_id=task.source_component.codesystem_id_id,
            task__source_component__component_id__in=exclude_components,
        ).values_list("code", flat=True)

        return MappingECLConcept.objects.filter(
            task_id=self.kwargs["task_pk"]
        ).exclude(
            code__in=exclusions
        ).select_related("ecl").order_by("is_new", "is_deleted", "ecl_id")


class MappingProjectAuditListAPIView(ListAPIView, UpdateAPIView):
    serializer_class = MappingProjectAuditSerializer
    permission_classes = [
        MappingProjectAccessPermission,
    ]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, django_filters.rest_framework.DjangoFilterBackend]

    filterset_fields = ["ignore", "hit_reason",]
    search_fields = ["comment", "hit_reason", "extra_1", "extra_2"]
    ordering_fields = ["hit_reason", "ignore", "audit_type", "first_hit_time", "comment"]

    def get_queryset(self):
        return MappingProjectAudit.objects.filter(project_id=self.kwargs["project_pk"])

    def get_object(self):
        queryset = self.get_queryset()

        return get_object_or_404(queryset, pk=self.kwargs["hit_id"])
