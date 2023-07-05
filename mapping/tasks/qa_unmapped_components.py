
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from mapping.enums import ProjectAuditTypes
from mapping.models import MappingCodesystemComponent, MappingProject, MappingProjectAudit, MappingTask, MappingECLConcept
from terminologieserver.client import TerminiologieClient, TerminologieRequestError


@shared_task
def unmapped_components():
    """Find unmapped components and create MappingProjectAudit records for each component."""

    logger = get_task_logger(__name__)

    def get_concept_codes(task: MappingTask) -> int:
        """Get list of concepts codes for any given task.

        Args:
            task (MappingTask): Task instance.

        Returns:
            Number of concept codes.
        """
        exclude_components = [] if task.exclusions is None else task.exclusions

        try:
            remote_exclusion = task.mappingeclpartexclusion_set.all()[0]
        except IndexError:
            remote_exclusion = None
        if remote_exclusion is not None:
            exclude_components = list(set(exclude_components + remote_exclusion.components))

        exclusions = MappingECLConcept.objects.filter(
            task__project_id=task.project_id_id,
            task__source_component__codesystem_id_id=task.source_component.codesystem_id_id,
            task__source_component__component_id__in=exclude_components,
        ).values_list("code", flat=True)

        return MappingECLConcept.objects.filter(
            task_id=task.id
        ).exclude(
            code__in=exclusions
        ).count()

    client = TerminiologieClient()
    try:
        client.login()
    except TerminologieRequestError as e:
        logger.error(f"Failed to login to terminologie.nl: {e}")
        return

    for project in MappingProject.objects.all():
        # Clear all audits.
        MappingProjectAudit.objects.filter(project=project).exclude(ignore=True).delete()

        project_codes = []
        project_tasks = MappingTask.objects.filter(
            project_id=project
        ).select_related("source_component").prefetch_related("mappingeclpartexclusion_set")
        for task in project_tasks:
            codes = get_concept_codes(task=task)
            if codes > 0:
                project_codes.append(task.source_component_id)

        # Find all codes in scope
        if project.ecl_scope:
            expansion_result = client.yield_snomed_ecl_valueset(ecl_query=project.ecl_scope)
            for concept in expansion_result:
                if concept["code"] not in project_codes:
                    create_audit(project=project, code=concept["code"], extra_1=concept["display"])
        else:
            components = MappingCodesystemComponent.objects.filter(codesystem_id=project.source_codesystem).exclude(component_id__in=project_codes)
            for component in components:
                create_audit(project=project, code=component.component_id, extra_1=component.component_title)


def create_audit(project, code, extra_1=None, extra_2=None):
    """Create project audit record.

    Args:
        project (MappingProject): Project to create audit record for
        code (str): Concept Code to create audit for
    """
    MappingProjectAudit.objects.get_or_create(
        project=project,
        audit_type=ProjectAuditTypes.unmapped_component.value,
        extra_1=extra_1,
        extra_2=extra_2,
        hit_reason=f"Concept {code} is niet gemapt."
    )
