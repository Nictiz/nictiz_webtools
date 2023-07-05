from rest_framework.test import APITestCase

from app.factories import UserFactory, GroupFactory

from mapping.enums import MappingGroups
from mapping.factories import MappingProjectFactory, MappingTaskFactory, MappingECLConceptFactory


class MappingECLConceptViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.project_access_group = GroupFactory(name=MappingGroups.project_access)
        self.user.groups.add(self.project_access_group)
        self.client.force_login(self.user)
        self.project = MappingProjectFactory()
        self.project.access.add(self.user)
        self.task = MappingTaskFactory(project_id=self.project)

        self.url = "/mapping/api/1.0/projects/"
        self.test_url = f"{self.url}{self.project.pk}/tasks/{self.task.pk}/results/"

    def test_access_success(self):
        result = self.client.get(self.test_url)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(
            result.json(),
            {
                "count": 0,
                "previous": None,
                "next": None,
                "results": []
            }
        )

    def test_access_no_group_access(self):
        self.user.groups.clear()
        result = self.client.get(self.test_url)
        self.assertEqual(result.status_code, 403)

    def test_access_no_project_access(self):
        self.project.access.clear()

        result = self.client.get(self.test_url)
        self.assertEqual(result.status_code, 403)

    def test_output(self):
        concept = MappingECLConceptFactory(task=self.task)
        result = self.client.get(self.test_url)
        self.assertEqual(
            result.json(),
            {
                "count": 1,
                "previous": None,
                "next": None,
                "results": [
                    {
                        "code": concept.code,
                        "moduleId": concept.module_id,
                        "effectiveTime": concept.effective_time,
                        "definitionStatus": concept.definition_status,
                        "idAndFsnTerm": concept.id_and_fsn_term,
                        "active": concept.active,
                        "pt": {"term": concept.preferred_title, "lang": concept.pt_lang},
                        "fsn": {"term": concept.fsn, "lang": concept.fsn_lang},
                        "queryId": str(concept.ecl_id),
                        "query": concept.ecl.query,
                        "description": concept.ecl.description,
                        "correlation": concept.ecl.mapcorrelation,
                        "status": "existing"
                    }
                ]
            }
        )
