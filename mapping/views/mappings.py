import json
import sys
import time
import uuid

# import environ
import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions

from mapping.tasks import (
    createRulesFromEcl,
    createRulesForAllTasks,
    send_task,
    update_ecl_task
)
from mapping.models import (
    MappingProject,
    MappingTask,
    MappingEclPart,
    MappingEclPartExclusion,
    MappingRule,
    MappingCodesystem,
    MappingCodesystemComponent,
)


class Permission_MappingProject_Access(permissions.BasePermission):
    """
    Global permission check rights to use the RC Audit functionality.
    """

    def has_permission(self, request, view):
        if "mapping | access" in request.user.groups.values_list("name", flat=True):
            return True


class Permission_MappingProject_ChangeMappings(permissions.BasePermission):
    """
    Global permission check rights to change mappings.
    """

    def has_permission(self, request, view):
        if "mapping | edit mapping" in request.user.groups.values_list(
            "name", flat=True
        ):
            return True


class Permission_Secret(permissions.BasePermission):
    """
    Global permission check rights to use the taskmanager.
    """

    def has_permission(self, request, view):
        if str(request.GET.get("secret")) != settings.MAPPING_API_SECRETS:
            print("Incorrect or absent secret")
            return False
        else:
            return True


class MappingTaskReset(viewsets.ViewSet):
    """
    Destroys most of the things about an ECL-1 task that can hang up the system.
    - Rules
    - ECL queries and its results
    """

    permission_classes = [Permission_MappingProject_ChangeMappings]

    def retrieve(self, request, pk=None):
        if pk is not None:
            print(
                f"[mappings/MappingTaskReset retrieve] requested by {request.user} - {pk}"
            )

            task = MappingTask.objects.get(id=pk)

            if task.project_id.project_type == "4":
                print(f"[mappings/MappingTaskReset retrieve] resetting ecl_parts")
                result = MappingEclPart.objects.filter(task=task).delete()
                print(
                    f"[mappings/MappingTaskReset retrieve] resetting ecl_parts result: {result}"
                )

                print(f"[mappings/MappingTaskReset retrieve] removing rules")
                rules = MappingRule.objects.filter(
                    project_id=task.project_id.id,
                    target_component=task.source_component,
                )
                print(f"Found {rules.count()} rules - now deleting.")
                result = rules.delete()
                print(
                    f"[mappings/MappingTaskReset retrieve] removing rules result: {result}"
                )

                # Disabled on request
                # print(f"[mappings/MappingTaskReset retrieve] removing exclusions")
                # result = MappingEclPartExclusion.objects.filter(task = task).delete()
                # print(f"[mappings/MappingTaskReset retrieve] removing exclusions result: {result}")
            else:
                print(f"Eh.. Nothing to do for a non-ECL task.")

            return Response(f"Task reset completed for task id {pk}")
        else:
            return Response("No id = no reset")


class MappingTargetSearch(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_Access]

    def create(self, request):
        print(
            f"[mappings/MappingTargetSearch create] requested by {request.user} - data: {str(request.data)[:500]}"
        )
        query = request.data.get("query").strip()
        print(
            request.user.username,
            ": mappings/MappingTargetSearch : Searching for",
            query,
        )

        output = []

        ##### Single word search disabled
        # # Start with the best matches: single word postgres match
        # snomedComponents = MappingCodesystemComponent.objects.filter(
        #     Q(component_id__icontains=query) |
        #     Q(component_title__icontains=query)
        # ).select_related(
        #     'codesystem_id',
        # )

        ##### Search exact component_id
        snomedComponents = MappingCodesystemComponent.objects.filter(
            component_id=query
        ).select_related(
            "codesystem_id",
        )

        for result in snomedComponents:
            try:
                if (result.component_extra_dict.get("Actief", False) == "True") or (
                    result.component_extra_dict.get("Actief", False) == True
                ):
                    active = "Ja"
                else:
                    active = "Nee"
            except:
                active = "Onbekend"
            output.append(
                {
                    "text": f"{result.codesystem_id.codesystem_title} {result.component_id} - {result.component_title} [Actief: {active}]",
                    "value": result.id,
                    "component": {
                        "id": result.id,
                        "component_id": result.component_id,
                        "title": result.component_title,
                    },
                    "codesystem": {
                        "title": result.codesystem_id.codesystem_title,
                        "version": result.codesystem_id.codesystem_version,
                    },
                    "extra": result.component_extra_dict,
                }
            )
        ###### Full text search disabled
        # # In addition, full text search if needed
        # if len(output) == 0:
        #     snomedComponents = MappingCodesystemComponent.objects.annotate(search=SearchVector('component_title','component_id',),).filter(search=query)
        #     for result in snomedComponents:
        #         output.append({
        #             'text' : result.component_title,
        #             'value': result.component_id,
        #             'component': {'id':result.id, 'title':result.component_title},
        #             'codesystem': {'title': result.codesystem_id.codesystem_title, 'version': result.codesystem_id.codesystem_version},
        #             'extra': result.component_extra_dict,
        #         })
        # output = sorted(output, key=lambda item: len(item.get("text")), reverse=False)
        return Response(output)


class RuleSearchByComponent(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_Access]

    def create(self, request):
        print(
            f"[mappings/RuleSearchByComponent create] requested by {request.user} - data: {str(request.data)[:500]}"
        )
        query = request.data.get("query")
        print(
            request.user.username,
            ": mappings/RuleSearchByComponent : Searching for",
            query,
        )

        component = MappingCodesystemComponent.objects.get(id=query)

        output = []

        target = MappingRule.objects.filter(target_component=component)
        for rule in target:
            tasks = MappingTask.objects.filter(source_component=rule.source_component)
            for task in tasks:
                output.append(
                    {
                        "task_id": task.id,
                        "project": task.project_id.title,
                        "project_id": task.project_id.id,
                        "rule_id": rule.id,
                        "source_id": rule.source_component.component_id,
                        "source_title": rule.source_component.component_title,
                        "target_id": rule.target_component.component_id,
                        "target_title": rule.target_component.component_title,
                    }
                )

        source = MappingRule.objects.filter(source_component=component)
        for rule in source:
            tasks = MappingTask.objects.filter(source_component=rule.source_component)
            for task in tasks:
                output.append(
                    {
                        "task_id": task.id,
                        "project": task.project_id.title,
                        "project_id": task.project_id.id,
                        "rule_id": rule.id,
                        "source_id": rule.source_component.component_id,
                        "source_title": rule.source_component.component_title,
                        "target_id": rule.target_component.component_id,
                        "target_title": rule.target_component.component_title,
                    }
                )

        return Response(output)


class MappingDialog(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_Access]

    def retrieve(self, request, pk=None):
        print(f"[mappings/MappingDialog retrieve] requested by {request.user} - {pk}")
        print("Retrieving mappingrule", pk)
        if pk != "extra":
            mapping = MappingRule.objects.get(id=pk)
            output = {
                "id": mapping.id,
                "codesystem": {
                    "title": mapping.target_component.codesystem_id.codesystem_title,
                    "version": mapping.target_component.codesystem_id.codesystem_version,
                },
                "component": {
                    "id": mapping.target_component.component_id,
                    "title": mapping.target_component.component_title,
                    "extra": mapping.target_component.component_extra_dict,
                },
            }
        else:
            output = {
                "id": "extra",
                "codesystem": {
                    "title": None,
                    "version": None,
                },
                "component": {
                    "id": None,
                    "title": "Nieuwe mapping",
                    "extra": None,
                },
            }
        return Response(output)

    def create(self, request):
        print(
            f"[mappings/MappingDialog create] requested by {request.user} - data: {str(request.data)[:500]}"
        )
        if "mapping | edit mapping" in request.user.groups.values_list(
            "name", flat=True
        ):
            print(f"[MappingDialog/create] @ {request.user.username}")
            print(f"Data: {request.data}")

            if request.data.get("new"):
                print("Target is bekend - uitvoeren")
                task = MappingTask.objects.get(id=request.data.get("task"))
                current_user = User.objects.get(id=request.user.id)
                if MappingProject.objects.get(
                    id=task.project_id.id, access__username=current_user
                ):
                    try:
                        if task.project_id.project_type == "1":  # One to many
                            source_component = MappingCodesystemComponent.objects.get(
                                id=task.source_component.id
                            )
                            target_component = MappingCodesystemComponent.objects.get(
                                id=request.data.get("new").get("component").get("id")
                            )
                            print("Project type 1")
                        elif task.project_id.project_type == "2":  # Many to one
                            source_component = MappingCodesystemComponent.objects.get(
                                id=request.data.get("new").get("component").get("id")
                            )
                            target_component = MappingCodesystemComponent.objects.get(
                                id=task.source_component.id
                            )
                            print("Project type 2")
                        elif task.project_id.project_type == "4":  # ECL to one
                            source_component = MappingCodesystemComponent.objects.get(
                                id=request.data.get("new").get("component").get("id")
                            )
                            target_component = MappingCodesystemComponent.objects.get(
                                id=task.source_component.id
                            )
                            print("Project type 4")
                        else:
                            print(
                                "No support for this project type in MappingDialog POST method [type 3?]"
                            )
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        error = "Exc [MappingDialog/create] error type: {} \n TB: {}".format(
                            exc_type, exc_tb.tb_lineno
                        )
                        print(error)

                    print("Mapping:", request.data.get("mapping"), "\n\n")
                    if request.data.get("mapping").get("id") == "extra":
                        print("ID=extra -> Zou een nieuwe mapping moeten worden.")
                        print("Task", request.data.get("task"))
                        print(
                            "Creating new mapping to component",
                            request.data.get("new").get("component").get("id"),
                        )

                        # Fetch the existing rules, ordered by group > priority
                        existing_rules = MappingRule.objects.filter(
                            project_id=task.project_id,
                            source_component=task.source_component,
                        ).order_by("mapgroup", "mappriority")

                        new_target = MappingCodesystemComponent.objects.get(
                            id=request.data.get("new").get("component").get("id")
                        )

                        if existing_rules.exists():
                            mapping = MappingRule.objects.create(
                                project_id=task.project_id,
                                source_component=task.source_component,
                                target_component=new_target,
                                mapgroup=(
                                    existing_rules.last().mapgroup
                                ),  # Prefill the group with highest existing group
                                mappriority=(
                                    existing_rules.last().mappriority + 1
                                ),  # Prefill the priority with highest existing priority + 1
                                active=True,
                            )
                        else:
                            mapping = MappingRule.objects.create(
                                project_id=task.project_id,
                                source_component=task.source_component,
                                target_component=new_target,
                                mapgroup=1,
                                mappriority=1,
                                active=True,
                            )
                        mapping.save()
                    else:
                        print("Betreft bestaande mapping.")
                        print(
                            "Replacing mapping",
                            request.data.get("mapping", {}).get("id"),
                        )
                        print(f"New target: {request.data.get('new')}")
                        print(f"Target is ingesteld - wordt aangepast")
                        mapping = MappingRule.objects.get(
                            id=request.data.get("mapping").get("id")
                        )
                        new_target = MappingCodesystemComponent.objects.get(
                            id=request.data.get("new").get("component").get("id")
                        )
                        mapping.target_component = new_target
                        mapping.save()
                        print(f"Mapping object: {str(mapping)}")

                    print("Start audit")
                    send_task(
                        "mapping.tasks.qa_orchestrator.audit_async",
                        ["multiple_mapping", task.project_id.id, task.id],
                        {},
                    )

                return Response(str(mapping))
            else:
                print("Target is niet bekend - geen actie ondernomen")
                return Response(None)
        else:
            return Response("Geen toegang", status=status.HTTP_401_UNAUTHORIZED)


class MappingExclusions(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_ChangeMappings]

    def create(self, request):
        print(
            f"[mappings/MappingExclusions create] requested by {request.user} - data: {str(request.data)[:500]}"
        )
        print(f"[MappingExclusions/create] @ {request.user.username} - {request.data}")
        output = True
        try:
            if "mapping | edit mapping" in request.user.groups.values_list(
                "name", flat=True
            ):
                print(f"[MappingExclusions/create] @ {request.user.username} => Go")
                task = MappingTask.objects.get(id=request.data.get("payload").get("id"))

                # Edgecase check: check if there are multiple exclusion records for this task
                exclusions = MappingEclPartExclusion.objects.filter(task=task)
                if exclusions.count() > 1:
                    # if so: delete
                    exclusions.delete()
                # Select or create a new one
                obj, created = MappingEclPartExclusion.objects.get_or_create(task=task)

                exclusion_list = list(
                    request.data.get("payload")
                    .get("exclusions", {})
                    .get("string")
                    .split("\n")
                )
                obj.components = sorted(exclusion_list)
                obj.save()
                print(obj, created)
            else:
                print(
                    f"[MappingExclusions/create] @ {request.user.username} => No permission"
                )
        except Exception as e:
            error = (
                f"[MappingExclusions/create] @ {request.user.username} => error ({e})"
            )
            print(error)
            output = error

        return Response(output)


class ReverseMappingExclusions(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_Access]

    def retrieve(self, request, pk=None):
        print(
            f"[mappings/ReverseMappingExclusions retrieve] requested by {request.user} - {pk}"
        )
        result = None
        output = []
        try:
            if "mapping | view tasks" in request.user.groups.values_list(
                "name", flat=True
            ):
                component_id = MappingTask.objects.get(id=str(pk))

                exclusions = MappingEclPartExclusion.objects.filter(
                    components__contains=str(component_id.source_component.component_id)
                ).select_related("task", "task__source_component")
                for exclusion in exclusions:
                    output.append(
                        {
                            "task": exclusion.task.id,
                            "component_id": str(
                                exclusion.task.source_component.component_id
                            ),
                            "component_title": str(
                                exclusion.task.source_component.component_title
                            ),
                        }
                    )
            else:
                print(
                    f"[mappings/ReverseMappingExclusions retrieve] @ {request.user.username} => No permission"
                )
        except Exception as e:
            print(
                f"[mappings/ReverseMappingExclusions retrieve] @ {request.user.username} => error ({e})"
            )

        return Response(output)


class RemoveMappingExclusions(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_Access]

    def create(self, request):
        print(
            f"[mappings/RemoveMappingExclusions create] requested by {request.user} - data: {str(request.data)[:500]}"
        )

        try:
            if "mapping | view tasks" in request.user.groups.values_list(
                "name", flat=True
            ):
                data = request.data.get("payload")
                task = MappingTask.objects.get(id=data.get("task"))
                remote_exclusions = MappingEclPartExclusion.objects.get(
                    task=task,
                )

                _components = remote_exclusions.components
                print(
                    f"[RemoveMappingExclusions/create] @ {request.user.username} - Old list: {_components}"
                )
                _components.remove(data.get("component"))
                remote_exclusions.components = _components
                remote_exclusions.save()
                print(
                    f"[RemoveMappingExclusions/create] @ {request.user.username} - Result: {remote_exclusions.components}"
                )

            else:
                print(
                    f"[ReverseMappingExclusions/create] @ {request.user.username} => No permission"
                )
        except Exception as e:
            print(
                f"[ReverseMappingExclusions/create] @ {request.user.username} => error ({e})"
            )

        return Response(request.data["payload"]["task"])


class AddRemoteExclusion(viewsets.ViewSet):
    """Will add an exclusion for the current task to a different task."""

    """     Usecase: Working on code A, you want to add an exclusion to task B for code A   """
    permission_classes = [Permission_MappingProject_ChangeMappings]

    def create(self, request, pk=None):
        print(
            f"[mappings/AddRemoteExclusion create] requested by {request.user} - data: {str(request.data)[:500]}"
        )

        result = None
        try:
            output = []
            if "mapping | edit mapping" in request.user.groups.values_list(
                "name", flat=True
            ):
                payload = request.data.get("payload")
                print(
                    f"[AddRemoteExclusion/create] @ {request.user.username} => Go. Payload: {payload}"
                )
                task = MappingTask.objects.get(id=payload.get("task"))

                remote_task = MappingTask.objects.get(
                    source_component__component_id=payload.get("sourceComponent"),
                    project_id=task.project_id,
                )
                try:
                    remote_exclusions = MappingEclPartExclusion.objects.get(
                        task=remote_task,
                    )

                    print(
                        f"[AddRemoteExclusion/create] @ {request.user.username} => Exclusie-object bestaat."
                    )
                    if remote_exclusions.components == None:
                        print(
                            f"[AddRemoteExclusion/create] @ {request.user.username} => Exclusie-object bestaat, met foutieve inhoud (None)."
                        )
                        remote_exclusions.components = []

                    excl_list = remote_exclusions.components
                    if payload["targetComponent"] not in excl_list:
                        print(
                            f"[AddRemoteExclusion/create] @ {request.user.username} => Exclusie-object bevatte dit component nog niet. Wordt aangevuld."
                        )
                        excl_list.append(payload["targetComponent"])
                    else:
                        print(
                            f"[AddRemoteExclusion/create] @ {request.user.username} => Exclusie-object bevatte dit component al."
                        )

                    remote_exclusions.save()

                except ObjectDoesNotExist:
                    print(
                        f"[AddRemoteExclusion/create] @ {request.user.username} => Exclusie-object bestond nog niet. Wordt aangemaakt."
                    )
                    remote_exclusions = MappingEclPartExclusion.objects.create(
                        task=remote_task, components=[payload.get("targetComponent")]
                    )
                    remote_exclusions.save()
                print(
                    f"[AddRemoteExclusion/create] @ {request.user.username} => Result: {remote_exclusions.task.source_component.component_id} => {remote_exclusions.components}"
                )
                output = remote_exclusions.task.id
            else:
                print(
                    f"[AddRemoteExclusion/create] @ {request.user.username} => No permission"
                )
        except Exception as e:
            print(
                f"[AddRemoteExclusion/create] @ {request.user.username} => error ({e})"
            )

        return Response(output)


class MappingTargetFromReverse(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_Access]

    def create(self, request):
        print(
            f"[mappings/MappingTargetFromReverse create] requested by {request.user} - data: {str(request.data)[:500]}"
        )

        try:
            if "mapping | edit mapping" in request.user.groups.values_list(
                "name", flat=True
            ):
                payload = request.data.get("payload")
                task = MappingTask.objects.get(id=payload.get("taskid"))
                if task.user == request.user:
                    if task.project_id.project_type == "1":
                        component = MappingCodesystemComponent.objects.get(
                            component_id=payload.get("conceptid"),
                            codesystem_id__id=payload.get("codesystem"),
                        )
                        obj = MappingRule.objects.create(
                            project_id=task.project_id,
                            source_component=task.source_component,
                            target_component=component,
                        )
                        return Response(
                            f"[MappingTargetFromReverse/create] @ {request.user.username} - Succes"
                        )
                    else:
                        return Response(
                            f"[MappingTargetFromReverse/create] @ {request.user.username} - Not supported for projects other than 1-N"
                        )
                else:
                    return Response(
                        f"[MappingTargetFromReverse/create] @ {request.user.username} - Not allowed: not your task?"
                    )
            else:
                return Response(
                    f"[MappingTargetFromReverse/create] @ {request.user.username} - Geen toegang"
                )
        except Exception as e:
            return Response(
                f"[MappingTargetFromReverse/create] @ {request.user.username} - Error: {str(e)}"
            )


class MappingTargets(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_Access]

    def create(self, request):
        print(
            f"[mappings/MappingTargets create] requested by {request.user} - data: {str(request.data)[:500]}"
        )

        try:
            if "mapping | edit mapping" in request.user.groups.values_list(
                "name", flat=True
            ):
                # print(str(request.data)[:100],"........")
                task = MappingTask.objects.get(id=request.data.get("task"))
                current_user = User.objects.get(id=request.user.id)

                if (
                    MappingProject.objects.get(
                        id=task.project_id.id, access__username=current_user
                    )
                    and task.user == current_user
                ):
                    # Handle 1-Many mapping targets
                    if task.project_id.project_type == "1":
                        print("\n\n----------------------------------\n")
                        for target in request.data.get("targets"):
                            print("ID", target.get("target").get("id"))
                            print("NIEUW", target.get("target").get("new"))
                            print(
                                "component_id", target.get("target").get("component_id")
                            )
                            print(
                                "component_title",
                                target.get("target").get("component_title"),
                            )
                            print("rule", target.get("rule"))
                            print("correlation", target.get("correlation"))
                            print("advice", target.get("advice"))
                            print("group", target.get("group"))
                            print("priority", target.get("priority"))
                            print("dependency", target.get("dependency"))
                            print("DELETE", target.get("delete"))
                            print("")

                            if target.get("delete") == True:
                                print("Get ready to delete")
                                mapping_rule = MappingRule.objects.get(
                                    id=target.get("id")
                                )
                                print(mapping_rule)
                                mapping_rule.delete()
                                print(mapping_rule)
                            elif target.get("id") != "extra":
                                print("Aanpassen mapping", target.get("id"))
                                mapping_rule = MappingRule.objects.get(
                                    id=target.get("id")
                                )

                                mapping_rule.mapgroup = target.get("group")
                                mapping_rule.mappriority = target.get("priority")
                                mapping_rule.mapcorrelation = target.get("correlation")
                                mapping_rule.mapadvice = target.get("advice")
                                mapping_rule.maprule = target.get("rule")

                                # Handle specifies/dependency/rule binding
                                if target.get("dependency"):
                                    for dependency in target.get("dependency"):
                                        print("Handling", dependency)  # TODO debug
                                        # If binding should be true:
                                        # First check if the relationship exists in DB, otherwise create it.
                                        if dependency.get("binding"):
                                            # Check if binding does not exists in DB
                                            print("Binding should be present")
                                            if not mapping_rule.mapspecifies.filter(
                                                id=dependency.get("rule_id")
                                            ).exists():
                                                print(
                                                    "Binding (many to many) not present in DB - creating"
                                                )
                                                addrule = MappingRule.objects.get(
                                                    id=dependency.get("rule_id")
                                                )
                                                print(
                                                    "Adding relationship to rule",
                                                    addrule,
                                                )
                                                mapping_rule.mapspecifies.add(addrule)
                                                # Sanity check: success?
                                                if mapping_rule.mapspecifies.filter(
                                                    id=dependency.get("rule_id")
                                                ).exists():
                                                    print("Created")
                                                else:
                                                    print("Failed")
                                            else:
                                                print("Binding already present")
                                        # If binding should not exist:
                                        # Check if present, if so: remove
                                        else:
                                            print("Binding should not be present")
                                            # Check if binding exists in DB
                                            if mapping_rule.mapspecifies.filter(
                                                id=dependency.get("rule_id")
                                            ).exists():
                                                print(
                                                    "Binding (many to many) present in DB but should not be - removing"
                                                )
                                                remrule = MappingRule.objects.get(
                                                    id=dependency.get("rule_id")
                                                )
                                                mapping_rule.mapspecifies.remove(
                                                    remrule
                                                )
                                                # Sanity check: success?
                                                if mapping_rule.mapspecifies.filter(
                                                    id=dependency.get("rule_id")
                                                ).exists():
                                                    print("Still present")
                                                else:
                                                    print("Succesfully removed")
                                            else:
                                                print("Binding was already absent")
                                    print("Done handling dependency for", dependency)
                                mapping_rule.save()

                        send_task(
                            "mapping.tasks.qa_orchestrator.audit_async",
                            ["multiple_mapping", task.project_id.id, task.id],
                            {},
                        )

                        return Response([])
                    # Handle ECL-1 mapping targets
                    elif task.project_id.project_type == "4":
                        print(
                            "MappingTargets/create - Handling ECL-1 mapping targets for task",
                            task.id,
                        )

                        print(repr(request.data))
                        queries = request.data.get("targets").get("queries")
                        for query in queries:
                            print("Handling query", str(query)[:100], ".........")
                            if query.get("delete") == True:
                                print("delete query ", query.get("id"))
                                current_query = MappingEclPart.objects.get(
                                    id=query.get("id")
                                )
                                current_query.delete()
                            else:
                                if (
                                    query.get("id") == "extra"
                                    and query.get("description")
                                    and query.get("query")
                                    and query.get("correlation")
                                ):
                                    print(
                                        f"Creating new query with description {query.get('description')} and query {query.get('query')}"
                                    )
                                    currentQuery = MappingEclPart.objects.create(
                                        task=task,
                                        description=query.get("description"),
                                        query=query.get("query"),
                                        mapcorrelation=query.get("correlation"),
                                    )
                                    update_ecl_task.delay(
                                        currentQuery.id, query.get("query")
                                    )
                                elif (
                                    query.get("id") != "extra"
                                    and query.get("description")
                                    and query.get("query")
                                    and query.get("correlation")
                                ):
                                    print(f"Editing existing query {query.get('id')}")
                                    currentQuery = MappingEclPart.objects.get(
                                        id=query.get("id")
                                    )
                                    currentQuery.description = query.get("description")
                                    currentQuery.query = query.get("query")
                                    currentQuery.mapcorrelation = query.get(
                                        "correlation"
                                    )
                                    currentQuery.save()
                                    print(
                                        f"---\nUsed the following data for update:\nQuery: {query.get('query')}\nDescription: {query.get('description')}\nCorrelation: {query.get('correlation')}\n"
                                    )
                                    queryInDatabase = MappingEclPart.objects.get(
                                        id=query.get("id")
                                    )
                                    print(
                                        f"Update resulted in:\nQuery {queryInDatabase.id}: {queryInDatabase.query}\nDescription: {queryInDatabase.description}\nCorrelation: {queryInDatabase.mapcorrelation}\n---"
                                    )
                                    print("---")
                                    print(f"Handled {str(queryInDatabase)}")
                                    update_ecl_task.delay(
                                        currentQuery.id, query.get("query")
                                    )
                                else:
                                    print("Empty query?")

                        return Response(
                            {
                                "message": "ECL-1 targets",
                            }
                        )
                # Error - no access due to project or task requirements
                else:
                    return Response(
                        "Geen toegang. Niet jouw taak? Geen toegang tot het project?"
                    )
            # Error - no acces due to no rights
            else:
                return Response("Geen toegang tot -edit mapping-")
        except Exception as e:
            print("\n\nException caught")
            print("Request by", str(request.user))
            print(e)
            print("\n\n")

    def retrieve(self, request, pk=None):
        request_uuid = str(uuid.uuid4())
        requestStart = time.time()
        print(
            f"[mappings/MappingTargets retrieve] {request_uuid} | requested by {request.user} - {pk}"
        )
        task = MappingTask.objects.get(id=pk)
        current_user = User.objects.get(id=request.user.id)

        if MappingProject.objects.get(
            id=task.project_id.id, access__username=current_user
        ):
            # Handle 1-N mapping targets
            if task.project_id.project_type == "1":
                if task.project_id.project_type == "1":
                    mappings = MappingRule.objects.filter(
                        project_id=task.project_id,
                        source_component=task.source_component,
                    )
                elif task.project_id.project_type == "2":
                    mappings = MappingRule.objects.filter(
                        project_id=task.project_id,
                        source_component=task.source_component,
                    )
                mappings = mappings.order_by("mapgroup", "mappriority")
                mapping_list = []
                dependency_list = []
                for mapping in mappings:
                    mapcorrelation = mapping.mapcorrelation
                    # if mapcorrelation == "447559001": mapcorrelation = "Broad to narrow"
                    # if mapcorrelation == "447557004": mapcorrelation = "Exact match"
                    # if mapcorrelation == "447558009": mapcorrelation = "Narrow to broad"
                    # if mapcorrelation == "447560006": mapcorrelation = "Partial overlap"
                    # if mapcorrelation == "447556008": mapcorrelation = "Not mappable"
                    # if mapcorrelation == "447561005": mapcorrelation = "Not specified"
                    try:
                        extra = mapping.target_component.component_extra_dict
                    except:
                        extra = ""

                    # Add dependencies to list
                    # For each mapping rule in this task, add an item with true/false
                    for maprule in mappings:
                        if mapping.mapspecifies.filter(id=maprule.id).exists():
                            binding = True
                        else:
                            binding = False
                        if maprule is not mapping:
                            dependency_list.append(
                                {
                                    "rule_id": maprule.id,
                                    "source": maprule.target_component.component_title,
                                    "binding": binding,
                                }
                            )

                    mapping_list.append(
                        {
                            "id": mapping.id,
                            "source": {
                                "id": mapping.source_component.id,
                                "component_id": mapping.source_component.component_id,
                                "component_title": mapping.source_component.component_title,
                            },
                            "target": {
                                "id": mapping.target_component.id,
                                "component_id": mapping.target_component.component_id,
                                "component_title": mapping.target_component.component_title,
                                "extra": extra,
                                "codesystem": {
                                    "title": mapping.target_component.codesystem_id.codesystem_title,
                                    "version": mapping.target_component.codesystem_id.codesystem_version,
                                    "id": mapping.target_component.codesystem_id.id,
                                },
                                "new": {},
                            },
                            "group": mapping.mapgroup,
                            "priority": mapping.mappriority,
                            "correlation": mapping.mapcorrelation,
                            "advice": mapping.mapadvice,
                            "rule": mapping.maprule,
                            "dependency": dependency_list,
                            "delete": False,
                        }
                    )
                    dependency_list = []
                if (
                    task.project_id.project_type == "1"
                    or task.project_id.project_type == "2"
                ):
                    # Append extra empty mapping
                    dependency_list = []
                    for maprule in mappings:
                        dependency_list.append(
                            {
                                "rule_id": maprule.id,
                                "source": maprule.target_component.component_title,
                                "binding": False,
                            }
                        )
                    mapping_list.append(
                        {
                            "id": "extra",
                            "source": {
                                "id": task.source_component.id,
                                "component_id": task.source_component.component_id,
                                "component_title": task.source_component.component_title,
                            },
                            "target": {
                                "id": None,
                                "component_id": None,
                                "component_title": None,
                                "codesystem": {
                                    "title": None,
                                    "version": None,
                                    "id": None,
                                },
                            },
                            "group": None,
                            "priority": None,
                            "correlation": "447557004",
                            "advice": None,
                            "rule": None,
                            "dependency": dependency_list,
                            "delete": False,
                        }
                    )
                    dependency_list = []
                return Response(mapping_list)

            # Handle ECL-1 mapping targets
            elif task.project_id.project_type == "4":
                try:
                    ### Get all definitive mappings
                    mappings = MappingRule.objects.filter(
                        project_id=task.project_id,
                        target_component=task.source_component,
                    ).select_related(
                        "source_component",
                        "target_component",
                        "target_component__codesystem_id",
                    )
                    mappings = mappings.order_by("mapgroup", "mappriority")
                    print(
                        f"[mappings/MappingTargets retrieve] {request_uuid} | Found {mappings.count()} mapping rules at {time.time()-requestStart}."
                    )
                    mapping_list = []
                    dependency_list = []
                    general_errors = []
                    try:
                        extra = mapping.target_component.component_extra_dict
                    except:
                        extra = ""
                    for mapping in mappings:
                        mapping_list.append(
                            {
                                "id": mapping.id,
                                "source": {
                                    "id": mapping.source_component.id,
                                    "component_id": mapping.source_component.component_id,
                                    "component_title": mapping.source_component.component_title,
                                },
                                "target": {
                                    "id": mapping.target_component.id,
                                    "component_id": mapping.target_component.component_id,
                                    "component_title": mapping.target_component.component_title,
                                    "extra": extra,
                                    "codesystem": {
                                        "title": mapping.target_component.codesystem_id.codesystem_title,
                                        "version": mapping.target_component.codesystem_id.codesystem_version,
                                        "id": mapping.target_component.codesystem_id.id,
                                    },
                                },
                                "correlation": mapping.mapcorrelation,
                            }
                        )

                    # Retrieve results from components that should be excluded
                    exclude_componentIDs = []
                    excluded_componentIDs = []
                    try:
                        obj = MappingEclPartExclusion.objects.select_related(
                            "task",
                            "task__source_component",
                            "task__source_component__codesystem_id",
                        ).get(task=task)
                        components = MappingCodesystemComponent.objects.filter(
                            codesystem_id=obj.task.source_component.codesystem_id,
                            component_id__in=list(obj.components),
                        )
                        # print(f"[mappings/MappingTargets retrieve] requested by {request.user} - {pk} ## Will exclude ECL results from {str(components)}")
                        # Loop components
                        print(
                            f"[mappings/MappingTargets retrieve] {request_uuid} | Found {components.count()} components in exclusions at {time.time()-requestStart}."
                        )
                        for component in components:
                            # print(f"[mappings/MappingTargets retrieve] requested by {request.user} - {pk} ## Handling exclusion of {str(component)}")
                            # For each, retrieve their tasks, in this same project
                            exclude_tasks = MappingTask.objects.filter(
                                project_id=task.project_id, source_component=component
                            )
                            # print(f"[mappings/MappingTargets retrieve] requested by {request.user} - {pk} ## Found tasks: {str(exclude_tasks)}")

                            for exclude_task in exclude_tasks:
                                # print(f"[mappings/MappingTargets retrieve] requested by {request.user} - {pk} ## Handling exclude_task {str(exclude_task)}")
                                queries = MappingEclPart.objects.filter(
                                    task=exclude_task
                                )

                                for query in queries:
                                    # print(f"Found query result for {exclude_task.source_component.component_title}: [{str(query.result)}] \n{list(query.result.get('concepts'))}")
                                    try:
                                        for key, value in query.result.get(
                                            "concepts"
                                        ).items():
                                            exclude_componentIDs.append(
                                                {
                                                    "key": key,
                                                    "component": {
                                                        "component_id": exclude_task.source_component.component_id,
                                                        "title": exclude_task.source_component.component_title,
                                                    },
                                                }
                                            )
                                    except Exception as e:
                                        # print(f"[mappings/MappingTargets retrieve] requested by {request.user} - {pk} ## Issue tijdens uitlezen resultaten: {e}")
                                        True

                            # print(f"Next component - list is now: {exclude_componentIDs}\n\n")
                        # print(f"Full exclude list: {exclude_componentIDs}")
                    except Exception as e:
                        print(
                            f"[mappings/MappingTargets retrieve] {request_uuid} | requested by {request.user} - {pk}. Exception at {time.time()-requestStart} ## Unhandled exception reverse mappings: {e}"
                        )

                    # Get all ECL Queries - including cached snowstorm response
                    all_results = list()
                    query_list = list()
                    excluded_ids = [x["key"] for x in exclude_componentIDs]
                    queries = MappingEclPart.objects.filter(task=task).select_related("task").order_by("id")

                    queries_unfinished = False
                    mapping_list_unfinished = False
                    result_concept_ids = []
                    i = 0
                    print(
                        f"[mappings/MappingTargets retrieve] {request_uuid} | Start handling {len(queries)} individual queries at {time.time()-requestStart}."
                    )
                    for query in queries:
                        i += 1
                        print(
                            f"[mappings/MappingTargets retrieve] {request_uuid} | Query {i} - adding keys to list: result_concept_ids at {time.time()-requestStart}"
                        )
                        if query.result is not None:
                            result_concept_ids += list(query.result.get(
                                "concepts", {}
                            ).keys())

                        # Add all results to a list for easy viewing
                        print(
                            f"[mappings/MappingTargets retrieve] {request_uuid} | Query {i} - adding results of query to list: all_results + handling list excluded_componentIDs at {time.time()-requestStart}"
                        )
                        try:
                            # total time spent filtering
                            filter_time = 0
                            appending_time = 0
                            max_results = 4000
                            max_export = 20_000
                            print(
                                f"[mappings/MappingTargets retrieve] {request_uuid} | Query {i} - Fetching reason for exclusion for each excluded result. {query.result.get('numResults','-')} results found in current ECL query at {time.time()-requestStart}."
                            )
                            if int(query.result.get("numResults", 0)) > max_results:
                                print(
                                    f"[mappings/MappingTargets retrieve] {request_uuid} | Query {i} - {query.result.get('numResults','-')} results found. This is more than {max_results}: will skip checking the reason for exclusion and generate empty exclusion explanations. Time: {time.time()-requestStart}."
                                )
                            else:
                                for key, result in query.result.get("concepts").items():
                                    if key not in excluded_ids:
                                        _start = time.time()

                                        result.update({
                                            "queryId": query.id,
                                            "query": query.query,
                                            "description": query.description,
                                            "correlation": query.mapcorrelation,
                                        })

                                        all_results.append(result)

                                        _end = time.time()
                                        appending_time += _end - _start

                                    else:
                                        start = time.time()
                                        exclusion_reason = list(
                                            filter(
                                                lambda x: (x["key"] == key),
                                                exclude_componentIDs,
                                            )
                                        )

                                        result.update({
                                            "exclusion_reason": exclusion_reason,
                                        })

                                        end = time.time()
                                        filter_time += end - start

                                        excluded_componentIDs.append(result)

                                print(
                                    f"[mappings/MappingTargets retrieve] {request_uuid} | Query {i} - End exclusion handling at {time.time()-requestStart}. Spent a total of {filter_time} on filtering and {appending_time} on appending included concepts."
                                )

                        except:
                            print(
                                f"[mappings/MappingTargets retrieve] {request_uuid} | Exception at {time.time()-requestStart} while retrieve mappings: No results?"
                            )

                        print(
                            f"[mappings/MappingTargets retrieve] {request_uuid} | Query {i} - adding query details to list: query_list at {time.time()-requestStart}"
                        )
                        if query.finished == False:
                            queries_unfinished = True
                        if query.export_finished == False:
                            mapping_list_unfinished = True

                        if int(query.result.get("numResults", 0)) > max_export:
                            query_list.append(
                                {
                                    "id": query.id,
                                    "description": query.description,
                                    "query": query.query,
                                    "finished": query.finished,
                                    "error": f"De resultaten van deze query kunnen niet getoond worden door het grote aantal [>{max_export}] concepten. Als de query echt klopt - mail Sander. Het is wel mogelijk om regels aan te maken.",
                                    "failed": True,
                                    "numResults": query.result.get("numResults", "-"),
                                    "correlation": query.mapcorrelation,
                                }
                            )
                            general_errors.append(
                                f"De resultaten van query {query.id} [{query.description}] kunnen niet getoond worden door het grote aantal [>{max_export}] concepten. Als de query echt klopt - mail Sander. Het is wel mogelijk om regels aan te maken."
                            )
                        else:
                            query_list.append(
                                {
                                    "id": query.id,
                                    "description": query.description,
                                    "query": query.query,
                                    "finished": query.finished,
                                    "error": query.error,
                                    "failed": query.failed,
                                    "numResults": query.result.get("numResults", "-"),
                                    "correlation": query.mapcorrelation,
                                }
                            )

                    query_list.append(
                        {
                            "id": "extra",
                            "description": "",
                            "query": "",
                            "finished": False,
                            "error": False,
                            "failed": False,
                            "result": "",
                            "correlation": "447561005",
                        }
                    )

                    # Check for duplicates in ECL queries
                    # region
                    #### Method 1 : works, but slow
                    # duplicates_in_ecl = [x for i, x in enumerate(result_concept_ids) if i != result_concept_ids.index(x)]

                    #### Method 2 : seems to provide the same result, in about 1/5th of the time.
                    # deduped_ecl = set(result_concept_ids)
                    # ecl_dupes = []
                    # for sctid in deduped_ecl:
                    #     if result_concept_ids.count(sctid) > 1:
                    #         ecl_dupes.append(sctid)
                    # duplicates_in_ecl = ecl_dupes
                    duplicates_in_ecl = []
                    # endregion

                    print(
                        f"[mappings/MappingTargets retrieve] {request_uuid} | Preparing Response at {time.time()-requestStart}."
                    )

                    return Response(
                        {
                            "queries": query_list,  # List of ECL queries
                            "queries_unfinished": queries_unfinished,  # True if any queries have not returned from Snowstorm
                            "allResults": all_results,  # Results of all ECL queries combined in 1 list
                            # 'exclusion_list' : exclude_componentIDs,
                            "excluded": excluded_componentIDs,
                            "duplicates_in_ecl": duplicates_in_ecl,
                            "errors": general_errors,
                            "mappings": mapping_list,
                            "mappings_unfinished": mapping_list_unfinished,
                        }
                    )
                except Exception as e:
                    print(
                        f"[mappings/MappingTargets retrieve] {request_uuid} | requested by {request.user} - {pk} - ERROR at {time.time()-requestStart}: {e}"
                    )


class MappingEclToRules(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_ChangeMappings]

    def retrieve(self, request, pk=None):
        print(
            f"[mappings/MappingEclToRules retrieve] requested by {request.user} - {pk}"
        )
        print(
            request.user,
            "Creating mapping rules for ECL queries associated with task",
            pk,
        )

        celery = createRulesFromEcl.delay(
            taskid=pk,
        )
        return Response(str(celery))

    def create(self, request):
        print(
            f"[mappings/MappingEclToRules create] requested by {request.user} - {request.data}"
        )

        try:
            if "mapping | edit mapping" in request.user.groups.values_list(
                "name", flat=True
            ):
                project = MappingProject.objects.get(id=request.data.get("id"))

                print(f"[mappings/MappingEclToRules create] Project: {str(project)}")

                # Check if user has access to the project
                current_user = User.objects.get(id=request.user.id)
                if current_user in project.access.all():
                    print(f"[mappings/MappingEclToRules create] User has access")
                    # Check if it is an ECL-1 project
                    if project.project_type == "4":
                        print(f"[mappings/MappingEclToRules create] Fire")
                        celery = createRulesForAllTasks.delay(
                            project_id=project.id,
                        )

                return Response(True)

                # if task.user == request.user:
                #     if task.project_id.project_type == '4':
                #         component = MappingCodesystemComponent.objects.get(
                #             component_id=payload.get('conceptid'),
                #             codesystem_id__id=payload.get('codesystem'),
                #             )
                #         obj = MappingRule.objects.create(
                #             project_id = task.project_id,
                #             source_component = task.source_component,
                #             target_component = component,
                #         )
                #         return Response(f"[mappings/MappingEclToRules] @ {request.user.username} - Succes")
                #     else:
                #         return Response(f"[mappings/MappingEclToRules] @ {request.user.username} - Not supported for projects other than 1-N")
                # else:
                #     return Response(f"[mappings/MappingEclToRules] @ {request.user.username} - Not allowed: not your task?")
            else:
                print(
                    f"[mappings/MappingEclToRules] @ {request.user.username} - Geen toegang"
                )
                return Response(
                    f"[mappings/MappingEclToRules] @ {request.user.username} - Geen toegang"
                )
        except Exception as e:
            print(
                f"[mappings/MappingEclToRules] @ {request.user.username} - Error: {str(e)}"
            )
            return Response(
                f"[mappings/MappingEclToRules] @ {request.user.username} - Error: {str(e)}"
            )


class MappingRemoveRules(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_ChangeMappings]

    def retrieve(self, request, pk=None):
        print(
            f"[mappings/MappingRemoveRules retrieve] requested by {request.user} - {pk}"
        )
        task = MappingTask.objects.get(id=str(pk))
        current_user = User.objects.get(id=request.user.id)
        if (
            MappingProject.objects.get(
                id=task.project_id.id, access__username=current_user
            )
        ) and (task.user == current_user):
            print(request.user, "Removing mapping rules associated with task", str(pk))

            rules = MappingRule.objects.filter(
                project_id=task.project_id,
                target_component=task.source_component,
            )
            count = rules.count()
            rules.delete()

            return Response(count)
        else:
            return Response("Nope - mag jij helemaal niet.")


class MappingReverse(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_Access]

    def retrieve(self, request, pk=None):
        print(f"[mappings/MappingReverse retrieve] requested by {request.user} - {pk}")
        task = MappingTask.objects.select_related(
            "project_id",
        ).get(id=pk)
        component = MappingCodesystemComponent.objects.get(id=task.source_component.id)
        if task.project_id.project_type == "1":
            reverse_mappings = MappingRule.objects.filter(
                target_component=component
            ).select_related("source_component")

            reverse = []
            for mapping in reverse_mappings:
                reverse.append(
                    {
                        "id": mapping.source_component.component_id,
                        "title": mapping.source_component.component_title,
                        "codesystem": {
                            "id": mapping.source_component.codesystem_id.id,
                            "title": mapping.source_component.codesystem_id.codesystem_title,
                        },
                        "correlation": mapping.mapcorrelation,
                    }
                )

        elif task.project_id.project_type == "4":
            reverse_mappings = MappingRule.objects.filter(
                source_component=component
            ).select_related("target_component", "target_component__codesystem_id")

            reverse = []
            for mapping in reverse_mappings:
                reverse.append(
                    {
                        "id": mapping.target_component.component_id,
                        "title": mapping.target_component.component_title,
                        "codesystem": {
                            "id": mapping.target_component.codesystem_id.id,
                            "title": mapping.target_component.codesystem_id.codesystem_title,
                        },
                        "correlation": mapping.mapcorrelation,
                    }
                )

        # output = " /".join(reverse)
        return Response(reverse)


class MappingRulesInvolvingCodesystem(viewsets.ViewSet):
    """
    Exporteert een lijst van alle componenten uit 1 codesysteem die gebruikt worden in een mapping rule.
    Er wordt hierbij geen rekening gehouden met de status van de betreffende taak; het kan ook een afgewezen taak zijn met een foutieve mapping.
    De status wordt in de export meegeleverd.
    Bedoeld om een overzicht te krijgen van alle gebruikte codes uit een stelsel.
    """

    permission_classes = [Permission_Secret]

    def retrieve(self, request, pk=None):
        print(
            f"[mappings/MappingRulesInvolvingCodesystem retrieve] requested by {request.user} - {pk}"
        )
        codesystem = MappingCodesystem.objects.get(id=pk)

        # Ophalen alle taken die dit codesystem gebruiken
        tasks = (
            MappingTask.objects.filter(source_codesystem__id=pk)
            .select_related(
                "user",
                "status",
                "project",
                "source_component",
                "source_component__codesystem_id",
            )
            .values(
                "id",
                "project_id__id",
                "project_id__title",
                "project_id__project_type",
                "source_component__id",
                "source_component__codesystem_id__codesystem_title",
                "source_component__component_id",
                "source_component__component_title",
                "status__status_title",
            )
        )

        components = [x["source_component__id"] for x in tasks]

        # Source
        rules = MappingRule.objects.filter(
            source_component__id__in=components
        ) | MappingRule.objects.filter(target_component__id__in=components)
        # Target
        rules = rules.select_related(
            "source_component",
            "source_component__codesystem_id",
            "target_component" "target_component__codesystem_id",
        ).values(
            "source_component__codesystem_id__codesystem_title",
            "source_component__component_id",
            "source_component__component_title",
            "target_component__codesystem_id__codesystem_title",
            "target_component__component_id",
            "target_component__component_title",
            "mapcorrelation",
        )

        # Compose output
        output = []
        for task in tasks:
            if task["project_id__project_type"] == "1":
                _rules = [
                    x
                    for x in rules
                    if x["source_component__component_id"]
                    == task["source_component__component_id"]
                ]
            elif task["project_id__project_type"] == "4":
                _rules = [
                    x
                    for x in rules
                    if x["target_component__component_id"]
                    == task["source_component__component_id"]
                ]

            # Translate the map correlation
            for _rule in _rules:
                correlation_options = [
                    ["447559001", "narrower"],
                    ["447557004", "equal"],
                    ["447558009", "wider"],
                    ["447560006", "inexact"],
                    ["447556008", "unmatched"],
                    ["447561005", "unmatched"],
                ]
                equivalence = _rule["mapcorrelation"]
                for code, readable in correlation_options:
                    try:
                        equivalence = equivalence.replace(code, readable)
                    except:
                        continue
                _rule.update({"mapcorrelation": equivalence})

            output.append(
                {
                    "task_id": task["id"],
                    "status": task["status__status_title"],
                    "project_id": task["project_id__id"],
                    "project_title": task["project_id__title"],
                    "component": {
                        "codesystem_title": task[
                            "source_component__codesystem_id__codesystem_title"
                        ],
                        "component_id": task["source_component__component_id"],
                        "component_title": task["source_component__component_title"],
                    },
                    "rules": _rules,
                }
            )

        return Response(output)


class MappingListLookup(viewsets.ViewSet):
    permission_classes = [Permission_MappingProject_Access]

    def create(self, request):
        print(
            f"[mappings/MappingListLookup create] requested by {request.user} - data: {str(request.data)[:500]}"
        )
        query = request.data.get("list")
        print(
            request.user.username,
            ": mappings/RuleSearchByComponent : Searching for",
            query,
        )

        list_source = []
        handled = []
        for ident in query.splitlines():
            print("get component", ident)

            # try:
            components = MappingCodesystemComponent.objects.filter(
                component_id=str(ident)
            )

            for component in components:
                # Identify rules using this component as either target or source
                _rules = MappingRule.objects.filter(source_component=component)
                _rules = _rules | MappingRule.objects.filter(target_component=component)

                # Loop over all source components in the above rules
                for _rule in _rules:
                    # Find tasks using this component as source
                    tasks = MappingTask.objects.filter(
                        source_component=_rule.source_component,
                        project_id__project_type="1",
                    )
                    for task in tasks:
                        if task.id not in handled:
                            rules = MappingRule.objects.filter(
                                source_component=task.source_component
                            ).order_by("mapgroup", "mappriority")
                            rule_list = []
                            for rule in rules:
                                mapcorrelation = rule.mapcorrelation
                                if mapcorrelation == "447559001":
                                    mapcorrelation = "Broad to narrow"
                                if mapcorrelation == "447557004":
                                    mapcorrelation = "Exact match"
                                if mapcorrelation == "447558009":
                                    mapcorrelation = "Narrow to broad"
                                if mapcorrelation == "447560006":
                                    mapcorrelation = "Partial overlap"
                                if mapcorrelation == "447556008":
                                    mapcorrelation = "Not mappable"
                                if mapcorrelation == "447561005":
                                    mapcorrelation = "Not specified"
                                rule_list.append(
                                    {
                                        "codesystem": rule.target_component.codesystem_id.codesystem_title,
                                        "id": rule.target_component.component_id,
                                        "title": rule.target_component.component_title,
                                        "group": rule.mapgroup,
                                        "priority": rule.mappriority,
                                        "correlation": mapcorrelation,
                                        "advice": rule.mapadvice,
                                    }
                                )
                            list_source.append(
                                {
                                    "project": task.project_id.title,
                                    "status": task.status.status_title,
                                    "task": task.id,
                                    "source": {
                                        "codesystem": task.source_component.codesystem_id.codesystem_title,
                                        "id": task.source_component.component_id,
                                        "title": task.source_component.component_title,
                                    },
                                    "targets": rule_list,
                                }
                            )
                        handled.append(task.id)

        return Response(list_source)


class MappingAutoMapNTS(viewsets.ViewSet):
    """
    Stuurt obv een taak ID een automap verzoek naar Ontoserver.
    """

    permission_classes = [Permission_MappingProject_Access]

    def retrieve(self, request, pk=None):
        timestamp = time.time()
        request_uuid = uuid.uuid4()
        print(
            f"[mappings/MappingAutoMapNTS retrieve] [{request_uuid}] requested by {request.user} - {pk}"
        )

        print(f"[mappings/MappingAutoMapNTS retrieve] [{request_uuid}] Fetch task data")
        task = MappingTask.objects.get(id=pk)
        search_string = task.source_component.component_title

        target_valueset = task.project_id.automap_valueset
        automap_method = task.project_id.automap_method
        if target_valueset == None:
            print(
                f"[mappings/MappingAutoMapNTS retrieve] [{request_uuid}] Geen valueset bekend voor dit project - afbreken"
            )
            return Response(
                "Geen valueset bekend voor dit project",
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            try:
                print(
                    f"[mappings/MappingAutoMapNTS retrieve] [{request_uuid}] Get access token"
                )

                data = data = {
                    "grant_type": "client_credentials",
                    "client_id": settings.NTS_CLIENT_ID,
                    "client_secret": settings.NTS_APIKEY,
                }
                token = requests.post(
                    "https://terminologieserver.nl/auth/realms/nictiz/protocol/openid-connect/token",
                    data=data,
                ).json()

                print(
                    f"[mappings/MappingAutoMapNTS retrieve] [{request_uuid}] Perform automap on [{search_string}] to [{target_valueset}]"
                )

                data = {
                    "resourceType": "Parameters",
                    "parameter": [
                        {
                            "name": "codeableConcept",
                            "valueCodeableConcept": {
                                "text": search_string,
                                "coding": [],
                            },
                        },
                        {"name": "target", "valueUri": target_valueset},
                        {
                            "name": "url",
                            "valueUri": f"http://ontoserver.csiro.au/fhir/ConceptMap/automapstrategy-{automap_method}",
                        },
                    ],
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token['access_token']}",
                }
                automap = requests.post(
                    "https://terminologieserver.nl/fhir/ConceptMap/$translate",
                    headers=headers,
                    data=json.dumps(data),
                ).json()

                # Handle output
                output = []
                for match in automap.get("parameter", []):
                    if match.get("name") == "match":
                        single_match = {
                            "concept": {},
                            "equivalence": None,
                        }
                        for part in match.get("part"):
                            if part["name"] == "concept":
                                single_match["concept"] = part["valueCoding"]

                                semantic_tag = (
                                    part["valueCoding"]
                                    .get("extension", [{}])[0]
                                    .get("valueString", None)
                                )
                                if semantic_tag == None:
                                    single_match["concept"]["semantic_tag"] = ""
                                else:
                                    single_match["concept"][
                                        "semantic_tag"
                                    ] = f" ({semantic_tag})"

                            if part["name"] == "equivalence":
                                single_match["equivalence"] = part["valueCode"]

                        output.append(single_match)

                print(f"mappings/MappingAutoMapNTS retrieve] [{request_uuid}] {output}")

                print(
                    f"[mappings/MappingAutoMapNTS retrieve] [{request_uuid}] Return response after {time.time() - timestamp}"
                )
                return Response(output)
            except Exception as e:
                return Response(str(e))
