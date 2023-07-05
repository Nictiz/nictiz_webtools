# Step 1: Add this file to __init__.py
# Step 2: Add your functions below.
# Step 3: Don't forget to fire the task somewhere if that is the intended use of this file.


# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger

from mapping.models import MappingProject, MappingTask, MappingTaskAudit
from mapping.tasks.qa_check_rule_attributes import check_rule_attributes
from mapping.tasks.qa_ecl_duplicates import check_duplicate_rules
from mapping.tasks.qa_ecl_vs_rules import ecl_vs_rules
from mapping.tasks.qa_labcodeset import labcodeset_order_as_source
from mapping.tasks.qa_nhg_labcodeset import nhg_loinc_order_vs_observation
from mapping.tasks.qa_recursive_exclusions import test_recursive_ecl_exclusion
from mapping.tasks.qa_snomed import snomed_daily_build_active

logger = get_task_logger(__name__)


@shared_task
def audit_async(audit_type=None, project=None, task_id=None):
    project = MappingProject.objects.get(id=project)
    if task_id == None:
        tasks = MappingTask.objects.select_related(
            "project_id",
            "source_component",
            "source_component__codesystem_id",
            "source_codesystem",
            "target_codesystem",
            "user",
            "status",
        ).filter(project_id=project)
    else:
        tasks = (
            MappingTask.objects.select_related(
                "project_id",
                "source_component",
                "source_component__codesystem_id",
                "source_codesystem",
                "target_codesystem",
                "user",
                "status",
            )
            .filter(project_id=project, id=task_id)
            .order_by("id")
        )

    num_tasks = tasks.count()

    ###### Slowly moving to separate audit QA scripts.
    logger.info(
        f"Orchestrator is spawning QA processes for {num_tasks} task(s) in project {project.id} - {project.title}"
    )

    # Spawn QA for labcodeset<->NHG tasks
    for task in tasks:
        logger.info("Handling taskID " + str(task.id))
        # Delete all old audit hits for this task if not whitelisted
        delete = MappingTaskAudit.objects.filter(
            task=task, ignore=False, sticky=False
        ).delete()

        # logger.info('Checking task: {0}'.format(task.id))
        check_rule_attributes.delay(taskid=task.id)

        # logger.info('Spawning QA scripts for Labcodeset)
        labcodeset_order_as_source.delay(taskid=task.id)

        # logger.info('Spawning QA scripts for NHG<->Labcodeset')
        nhg_loinc_order_vs_observation.delay(taskid=task.id)

        if task.project_id.project_type == "4":
            # logger.info('Spawning QA scripts for ECL-1 queries')
            if num_tasks > 1:
                print(
                    f"Skipping [mapping.tasks.qa_ecl_vs_rules.ecl_vs_rules] - only run this in project mode"
                )
                ecl_vs_rules.delay(taskid=task.id)
            check_duplicate_rules.delay(taskid=task.id)
            test_recursive_ecl_exclusion.delay(taskid=task.id)

        # logger.info('Spawning general QA scripts for SNOMED')
        # Snowstorm daily build SNOWSTORM does not like DDOS - only run on individual tasks, not on entire projects.
        if num_tasks == 1:
            print(
                f"Skipping [mapping.tasks.qa_snomed.snomed_daily_build_active] - only run this in single task mode"
            )
            snomed_daily_build_active.delay(taskid=task.id)
