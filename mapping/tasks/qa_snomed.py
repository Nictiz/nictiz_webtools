# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.utils.log import get_task_logger
from mapping.models import *
from snowstorm_client import Snowstorm

logger = get_task_logger(__name__)


@shared_task
def snomed_daily_build_active(taskid):
    logger.info("Spawned snomed_daily_build_active for TASK "+str(taskid))

    snowstorm = Snowstorm(
        baseUrl="https://dailybuild.ihtsdotools.org/snowstorm/snomed-ct",
        debug=True,
        preferredLanguage="en",
        defaultBranchPath="MAIN",
    )

    task = MappingTask.objects.get(id=taskid)
    mappings = MappingRule.objects.filter(project_id = task.project_id, source_component = task.source_component)

    # For each mapping rule associated with the selected task:
    for mapping in mappings:
        hit = False
        # If either of the codes is SNOMED:
        if (str(mapping.source_component.codesystem_id.codesystem_title).upper() == "SNOMED"):
            # Look for the code in the daily build browser of SI
            result = snowstorm.getConceptById(id=mapping.target_component.component_id)
            active = result.get('active')
            # print("CONCEPT IS:",active,"IN DAILY BUILD SI")
            if active == False:
                hit = True
        if (str(mapping.target_component.codesystem_id.codesystem_title).upper() == "SNOMED"):
            # Look for the code in the daily build browser of SI
            result = snowstorm.getConceptById(id=mapping.target_component.component_id)
            active = result.get('active')
            # print("CONCEPT IS:",active,"IN DAILY BUILD SI")
            if active == False:
                hit = True

        if hit:
            logger.info("That's a problem. Concept is inactief in daily build.")
            obj, created = MappingTaskAudit.objects.get_or_create(
                            task=task,
                            audit_type="snomed_daily_build_active",
                            hit_reason='Een van de gebruikte SNOMED concepten ['+str(mapping.target_component.component_id)+'] is inactief in de daily build van SNOMED International',
                        )
            logger.info(str(obj))
