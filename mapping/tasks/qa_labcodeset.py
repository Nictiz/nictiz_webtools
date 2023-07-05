# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger

from mapping.models import MappingTask, MappingTaskAudit

logger = get_task_logger(__name__)


@shared_task
def labcodeset_order_as_source(taskid):
    logger.info("Spawned labcodeset_order_as_source for TASK " + str(taskid))
    hit = False
    task = MappingTask.objects.get(id=taskid)

    # if task uses source_component as source
    if task.project_id.project_type == "1":
        # if source is labcodeset
        if task.source_component.codesystem_id.codesystem_title == "Labcodeset":
            # if source_component is an order
            if (
                task.source_component.component_extra_dict.get("Aanvraag/Resultaat")
                == "Order"
            ):
                hit = True

    if hit:
        obj, created = MappingTaskAudit.objects.get_or_create(
            task=task,
            audit_type="labcodeset_order_as_source",
            hit_reason="Labcodeset Order als bron voor taak",
        )
        logger.info(str(obj))
