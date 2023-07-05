from unittest import mock
from django.test import Client, TestCase

from app.factories import UserFactory, GroupFactory
from mapping.factories import MappingProjectFactory, MappingTaskFactory


class MappingTargetsViewSetTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()

        mapping_access_group = GroupFactory(name="mapping | access")
        mapping_edit_group = GroupFactory(name="mapping | edit mapping")

        self.user.groups.add(mapping_access_group)
        self.user.groups.add(mapping_edit_group)
        self.client.force_login(user=self.user)

        self.project = MappingProjectFactory()
        self.task = MappingTaskFactory(
            project_id=self.project,
            user=self.user,
        )

        self.project.access.add(self.user)

    def test_create_auth_required(self):
        self.client.logout()
        result = self.client.get(path=f"/mapping/api/1.0/mappings/{self.project.pk}/")
        self.assertEqual(result.status_code, 403)

    @mock.patch("mapping.views.mappings.update_ecl_task")
    def test_create_for_project_type_4(self, update_ecl1_task_mock):
        data = {
            "targets": {
                "queries": [
                    {
                        "id": "extra",
                        "description": "2342",
                        "query": "9847007 | Structure of hilum of adrenal gland (body structure) |",
                        "finished": False,
                        "error": False,
                        "failed": False,
                        "correlation": "447561005",
                    }
                ],
                "queries_unfinished": False,
                "duplicates_in_ecl": [],
                "errors": [],
                "mappings_unfinished": False,
            },
            "task": self.task.id,
        }
        result = self.client.post(
            path="/mapping/api/1.0/mappings/",
            data=data,
            content_type="application/json",
        )
        self.assertEqual(result.status_code, 200)

        self.assertEqual(
            update_ecl1_task_mock.mock_calls,
            [mock.call.delay(1, data["targets"]["queries"][0]["query"])],
        )
