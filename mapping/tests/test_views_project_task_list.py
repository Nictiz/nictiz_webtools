import json
from django.test import TestCase, RequestFactory

from app.factories import UserFactory, GroupFactory
from mapping.factories import MappingProjectFactory, MappingTaskFactory
from mapping.views.tasks import ProjectTasklist


class ProjectTasklistTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")
        self.user = UserFactory()
        project_access_group = GroupFactory(name="mapping | access")
        self.user.groups.add(project_access_group)
        self.request.user = self.user
        self.project = MappingProjectFactory()
        self.project.access.add(self.user)

    def test_permissions_check_not_logged(self):
        self.request.user = None
        self.project.access.clear()
        view = ProjectTasklist.as_view()

        result = view(self.request, project_pk=self.project.pk)

        self.assertEqual(result.status_code, 403)

    def test_permission_check_logged_but_no_access(self):
        self.project.access.clear()
        view = ProjectTasklist.as_view()

        result = view(self.request, project_pk=self.project.pk)

        self.assertEqual(result.status_code, 403)

    def test_permission_check_logged_and_project_access(self):
        view = ProjectTasklist.as_view()

        result = view(self.request, project_pk=self.project.pk)
        result.render()

        self.assertEqual(result.status_code, 200)
        self.assertEqual(
            result.data, {"count": 0, "previous": None, "next": None, "results": []}
        )

    def test_tasks_sorted_by_component_id_by_default(self):
        task1 = MappingTaskFactory(
            project_id=self.project,
            source_component__component_title="b",
            source_component__component_id=1,
        )
        task2 = MappingTaskFactory(
            project_id=self.project,
            source_component__component_title="a",
            source_component__component_id=2,
        )
        view = ProjectTasklist.as_view()

        result = view(self.request, project_pk=self.project.pk)
        result.render()

        self.assertEqual(
            result.data["results"][0]["component"]["id"],
            str(task1.source_component.component_id),
        )
        self.assertEqual(
            result.data["results"][1]["component"]["id"],
            str(task2.source_component.component_id),
        )

    def test_tasks_sorted_alphabetically(self):
        task1 = MappingTaskFactory(
            project_id=self.project,
            source_component__component_title="b",
            source_component__component_id=1,
        )
        task2 = MappingTaskFactory(
            project_id=self.project,
            source_component__component_title="a",
            source_component__component_id=2,
        )
        view = ProjectTasklist.as_view()

        with self.settings(PROJECTS_SORTED_ALPHABETICALLY=[self.project.pk]):
            result = view(self.request, project_pk=self.project.pk)
        result.render()

        self.assertEqual(result.data["count"], 2)
        self.assertEqual(
            result.data["results"][0]["component"]["id"],
            str(task2.source_component.component_id),
        )
        self.assertEqual(
            result.data["results"][1]["component"]["id"],
            str(task1.source_component.component_id),
        )

    def test_tasks_data_confirmed(self):
        task1 = MappingTaskFactory(
            project_id=self.project,
            source_component__component_title="b",
            source_component__component_id=1,
        )
        view = ProjectTasklist.as_view()

        result = view(self.request, project_pk=self.project.pk)
        result.render()

        self.assertEqual(result.data["count"], 1)
        self.assertEqual(
            json.loads(json.dumps(result.data["results"][0])),
            json.loads(
                json.dumps(
                    {
                        "id": task1.id,
                        "user": {
                            "id": "Niet toegewezen",
                            "username": "Niet toegewezen",
                            "name": "Niet toegewezen",
                        },
                        "component": {
                            "id": str(task1.source_component.component_id),
                            "title": task1.source_component.component_title,
                            "extra": None,
                            "codesystem": {
                                "id": task1.source_component.codesystem_id.id,
                                "version": str(
                                    task1.source_component.codesystem_id.codesystem_version
                                ),
                                "title": task1.source_component.codesystem_id.codesystem_title,
                            },
                        },
                        "exclusion": [],
                        "project": {"id": task1.project_id.id},
                        "status": {
                            "id": task1.status.id,
                            "title": task1.status.status_title,
                        },
                    }
                )
            ),
        )
