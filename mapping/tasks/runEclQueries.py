# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger

from mapping.models import MappingEclPart, MappingProject, MappingTask

logger = get_task_logger(__name__)


@shared_task
def runAllEclQueriesInProject(projectid):
    from mapping.tasks import update_ecl_task

    project = MappingProject.objects.get(id=projectid)
    logger.info(
        f"[runAllEclQueriesInProject] Started full-project run for project {project.title}"
    )
    tasks = MappingTask.objects.filter(project_id=project)
    for task in tasks:
        # Get all ECL queries for the task
        queries = MappingEclPart.objects.filter(task=task)
        for query in queries:
            update_ecl_task.delay(record_id=query.id, query=query.query, create_audit=True)
    logger.info("[runAllEclQueriesInProject] Finished")

    return True
