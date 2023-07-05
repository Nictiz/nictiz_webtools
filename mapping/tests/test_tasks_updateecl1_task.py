import json
from unittest import mock
from django.test import TestCase

from mapping.factories import MappingECLConceptFactory, MappingECLPartFactory
from mapping.tasks import UpdateECL1Task, update_ecl_task


class UpdateECL1TaskTestCase(TestCase):
    @mock.patch("mapping.tasks.tasks.requests")
    @mock.patch("mapping.tasks.tasks.time")
    def test_error_added_into_query(self, time_mock, requests_mock):
        requests_mock.get.side_effect = ValueError("Meh.")

        ecl_part = MappingECLPartFactory()

        result = UpdateECL1Task(record_id=ecl_part.pk, query="test")

        ecl_part.refresh_from_db()

        self.assertEqual(len(time_mock.mock_calls), 0)
        self.assertEqual(ecl_part.error, "Na 1 pogingen opgegeven: Meh.")
        self.assertTrue(ecl_part.failed)
        self.assertTrue(ecl_part.finished)

        self.assertEqual(result, str(ecl_part))

    @mock.patch("mapping.tasks.tasks.requests")
    @mock.patch("mapping.tasks.tasks.time")
    def test_400_error_stops_loop(self, time_mock, requests_mock):
        requests_mock.get.return_value.status_code = 400
        requests_mock.get.return_value.text = (
            '{"error": "very error", "message": "mucho details"}'
        )

        ecl_part = MappingECLPartFactory()

        UpdateECL1Task(record_id=ecl_part.pk, query="test")

        self.assertEqual(
            requests_mock.get.mock_calls,
            [
                mock.call(
                    "https://snowstorm.test-nictiz.nl/MAIN/SNOMEDCT-NL/concepts?activeFilter=true&limit=1000&ecl=test",
                    params={"Accept-Language": "nl"},
                )
            ],
        )

        ecl_part.refresh_from_db()

        self.assertEqual(len(time_mock.mock_calls), 0)
        self.assertTrue(ecl_part.failed)
        self.assertTrue(ecl_part.finished)
        self.assertEqual(
            ecl_part.error,
            'Na 1 pogingen opgegeven. Status code: 400. Response body: {"error": "very error", "message": "mucho details"}.',
        )

    @mock.patch("mapping.tasks.tasks.requests")
    @mock.patch("mapping.tasks.tasks.time")
    def test_500_error_stops_loop(self, time_mock, requests_mock):
        requests_mock.get.return_value.status_code = 500
        requests_mock.get.return_value.text = (
            '{"error": "very error", "message": "mucho details"}'
        )

        ecl_part = MappingECLPartFactory()

        UpdateECL1Task(record_id=ecl_part.pk, query="test")

        self.assertEqual(
            requests_mock.get.mock_calls,
            [
                mock.call(
                    "https://snowstorm.test-nictiz.nl/MAIN/SNOMEDCT-NL/concepts?activeFilter=true&limit=1000&ecl=test",
                    params={"Accept-Language": "nl"},
                )
            ],
        )

        ecl_part.refresh_from_db()

        self.assertEqual(len(time_mock.mock_calls), 0)
        self.assertTrue(ecl_part.failed)
        self.assertTrue(ecl_part.finished)
        self.assertEqual(
            ecl_part.error,
            'Na 1 pogingen opgegeven. Status code: 500. Response body: {"error": "very error", "message": "mucho details"}.',
        )

    @mock.patch("mapping.tasks.tasks.requests")
    @mock.patch("mapping.tasks.tasks.time")
    def test_500_error_non_json_parseable(self, time_mock, requests_mock):
        requests_mock.get.return_value.status_code = 500
        requests_mock.get.return_value.text = "non json error. mucho details"

        ecl_part = MappingECLPartFactory()

        UpdateECL1Task(record_id=ecl_part.pk, query="test")

        self.assertEqual(
            requests_mock.get.mock_calls,
            [
                mock.call(
                    "https://snowstorm.test-nictiz.nl/MAIN/SNOMEDCT-NL/concepts?activeFilter=true&limit=1000&ecl=test",
                    params={"Accept-Language": "nl"},
                )
            ],
        )

        ecl_part.refresh_from_db()

        self.assertEqual(len(time_mock.mock_calls), 0)
        self.assertTrue(ecl_part.failed)
        self.assertTrue(ecl_part.finished)
        self.assertEqual(
            ecl_part.error,
            "Na 1 pogingen opgegeven. Status code: 500. Response body: non json error. mucho details.",
        )

    @mock.patch("mapping.tasks.tasks.requests")
    @mock.patch("mapping.tasks.tasks.time")
    def test_non_200_response_is_retried(self, time_mock, requests_mock):
        requests_mock.get.return_value.status_code = 301
        requests_mock.get.return_value.text = "Forwarding to /dev/null"

        ecl_part = MappingECLPartFactory()

        UpdateECL1Task(record_id=ecl_part.pk, query="test")

        self.assertEqual(
            requests_mock.get.mock_calls[0],
            mock.call(
                "https://snowstorm.test-nictiz.nl/MAIN/SNOMEDCT-NL/concepts?activeFilter=true&limit=1000&ecl=test",
                params={"Accept-Language": "nl"},
            ),
        )
        self.assertEqual(len(requests_mock.get.mock_calls), 11)

        ecl_part.refresh_from_db()

        self.assertEqual(len(time_mock.mock_calls), 10)
        self.assertTrue(ecl_part.failed)
        self.assertTrue(ecl_part.finished)
        self.assertEqual(
            ecl_part.error,
            "Na 11 pogingen opgegeven. Status code: 301. Response body: Forwarding to /dev/null.",
        )

    @mock.patch("mapping.tasks.tasks.requests")
    @mock.patch("mapping.tasks.tasks.time")
    def test_200_response_is_saved(self, time_mock, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = {
            "total": 1,
            "items": [
                {
                    "conceptId": "9847007",
                    "active": True,
                    "definitionStatus": "PRIMITIVE",
                    "moduleId": "900000000000207008",
                    "effectiveTime": "20020131",
                    "fsn": {
                        "term": "Structure of hilum of adrenal gland (body structure)",
                        "lang": "en",
                    },
                    "pt": {"term": "Structure of hilum of adrenal gland", "lang": "en"},
                    "id": "9847007",
                    "idAndFsnTerm": "9847007 | Structure of hilum of adrenal gland (body structure) |",
                },
            ],
            "limit": 10000,
            "offset": 0,
            "searchAfter": "Wzk4NDcwMDdd",
            "searchAfterArray": [9847007],
        }

        ecl_part = MappingECLPartFactory()

        UpdateECL1Task(record_id=ecl_part.pk, query="test")

        self.assertEqual(
            requests_mock.get.mock_calls,
            [
                mock.call(
                    "https://snowstorm.test-nictiz.nl/MAIN/SNOMEDCT-NL/concepts?activeFilter=true&limit=1000&ecl=test",
                    params={"Accept-Language": "nl"},
                ),
                mock.call().json(),
            ],
        )

        ecl_part.refresh_from_db()

        self.assertEqual(len(time_mock.mock_calls), 0)
        self.assertFalse(ecl_part.failed)
        self.assertTrue(ecl_part.finished)
        self.assertIsNone(ecl_part.error)
        self.assertEqual(
            ecl_part.result,
            {
                "numResults": 1,
                "concepts": {
                    "9847007": {
                        "conceptId": "9847007",
                        "active": True,
                        "definitionStatus": "PRIMITIVE",
                        "moduleId": "900000000000207008",
                        "effectiveTime": "20020131",
                        "fsn": {
                            "term": "Structure of hilum of adrenal gland (body structure)",
                            "lang": "en",
                        },
                        "pt": {
                            "term": "Structure of hilum of adrenal gland",
                            "lang": "en",
                        },
                        "id": "9847007",
                        "idAndFsnTerm": "9847007 | Structure of hilum of adrenal gland (body structure) |",
                    }
                },
            },
        )

    @mock.patch("mapping.tasks.tasks.requests")
    @mock.patch("mapping.tasks.tasks.time")
    def test_paginated_response(self, time_mock, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.side_effect = [
            {
                "total": 2,
                "items": [
                    {
                        "conceptId": "9847007",
                        "active": True,
                        "definitionStatus": "PRIMITIVE",
                        "moduleId": "900000000000207007",
                        "effectiveTime": "20020131",
                        "fsn": {
                            "term": "Structure of hilum of adrenal gland (body structure)",
                            "lang": "en",
                        },
                        "pt": {
                            "term": "Structure of hilum of adrenal gland",
                            "lang": "en",
                        },
                        "id": "9847007",
                        "idAndFsnTerm": "9847007 | Structure of hilum of adrenal gland (body structure) |",
                    },
                ],
                "limit": 1,
                "offset": 0,
                "searchAfter": "Wzk4NDcwMDdd",
                "searchAfterArray": [9847007],
            },
            {
                "total": 2,
                "items": [
                    {
                        "conceptId": "9847008",
                        "active": True,
                        "definitionStatus": "PRIMITIVE",
                        "moduleId": "900000000000207008",
                        "effectiveTime": "20020131",
                        "fsn": {"term": "Second result", "lang": "en"},
                        "pt": {
                            "term": "Structure of hilum of adrenal gland",
                            "lang": "en",
                        },
                        "id": "9847008",
                        "idAndFsnTerm": "9847008 | Second result |",
                    },
                ],
                "limit": 1,
                "offset": 0,
                "searchAfter": "ASd23easdfAS",
                "searchAfterArray": [9847007],
            },
        ]

        ecl_part = MappingECLPartFactory()

        UpdateECL1Task(record_id=ecl_part.pk, query="test")

        self.assertEqual(
            requests_mock.get.mock_calls,
            [
                mock.call(
                    "https://snowstorm.test-nictiz.nl/MAIN/SNOMEDCT-NL/concepts?activeFilter=true&limit=1000&ecl=test",
                    params={"Accept-Language": "nl"},
                ),
                mock.call().json(),
                mock.call(
                    "https://snowstorm.test-nictiz.nl/MAIN/SNOMEDCT-NL/concepts?activeFilter=true&limit=1000&ecl=test&searchAfter=Wzk4NDcwMDdd",
                    params={"Accept-Language": "nl"},
                ),
                mock.call().json(),
            ],
        )

        ecl_part.refresh_from_db()

        self.assertEqual(len(time_mock.mock_calls), 0)
        self.assertFalse(ecl_part.failed)
        self.assertTrue(ecl_part.finished)
        self.assertIsNone(ecl_part.error)
        self.assertEqual(list(ecl_part.result.keys()), ["concepts", "numResults"])
        self.assertEqual(ecl_part.result["numResults"], 2)

        self.assertEqual(
            ecl_part.result["concepts"],
            {
                "9847007": {
                    "conceptId": "9847007",
                    "active": True,
                    "definitionStatus": "PRIMITIVE",
                    "moduleId": "900000000000207007",
                    "effectiveTime": "20020131",
                    "fsn": {
                        "term": "Structure of hilum of adrenal gland (body structure)",
                        "lang": "en",
                    },
                    "pt": {"term": "Structure of hilum of adrenal gland", "lang": "en"},
                    "id": "9847007",
                    "idAndFsnTerm": "9847007 | Structure of hilum of adrenal gland (body structure) |",
                },
                "9847008": {
                    "conceptId": "9847008",
                    "active": True,
                    "definitionStatus": "PRIMITIVE",
                    "moduleId": "900000000000207008",
                    "effectiveTime": "20020131",
                    "fsn": {"term": "Second result", "lang": "en"},
                    "pt": {"term": "Structure of hilum of adrenal gland", "lang": "en"},
                    "id": "9847008",
                    "idAndFsnTerm": "9847008 | Second result |",
                },
            },
        )

    @mock.patch("mapping.tasks.tasks.TerminiologieClient")
    def test_update_ecl_task_saving_all_new_concepts(self, term_client):
        term_client.return_value.expand_snomed_ecl_valueset.return_value = [
            {
                "code": "9847008",
                "moduleId": "900000000000207008",
                "system": "test1",
            }
        ]

        term_client.return_value.lookup_code.return_value = {
            "parameter": {}
        }
        term_client.return_value.params_to_dict.return_value = {
            "nl:900000000000003001": "structuur van hilum van bijnier (lichaamsstructuur)",
            "nl:preferredForLanguage": "structuur van hilum van bijnier",
            "en:display": "structuur van hilum van bijnier",
        }
        term_client.return_value.expanded_data_to_snowstorm_mapping.return_value = {
            "id": "9847008",
            "conceptId": "9847008",
            "moduleId": "900000000000207008",
            "effectiveTime": "20020131",
            "definitionStatus": "PRIMITIVE",
            "idAndFsnTerm": "9847008 | structuur van hilum van bijnier",
            "active": True,
            "fsn": {
                "lang": "en",
                "term": "structuur van hilum van bijnier (lichaamsstructuur)"
            },
            "pt": {
                "lang": "en",
                "term": "structuur van hilum van bijnier"
            },
        }

        ecl_part = MappingECLPartFactory()
        update_ecl_task(record_id=ecl_part.pk, query="test")

        self.assertEqual(ecl_part.concepts.count(), 1)
        concept = ecl_part.concepts.first()
        self.assertTrue(concept.is_new)

    @mock.patch("mapping.tasks.tasks.TerminiologieClient")
    def test_update_ecl_task_marking_concepts_as_existing(self, term_client):
        term_client.return_value.expand_snomed_ecl_valueset.return_value = [
            {
                "code": "9847008",
                "moduleId": "900000000000207008",
                "system": "test1",
            }
        ]

        term_client.return_value.lookup_code.return_value = {
            "parameter": {}
        }
        term_client.return_value.params_to_dict.return_value = {
            "nl:900000000000003001": "structuur van hilum van bijnier (lichaamsstructuur)",
            "nl:preferredForLanguage": "structuur van hilum van bijnier",
            "en:display": "structuur van hilum van bijnier",
        }
        term_client.return_value.expanded_data_to_snowstorm_mapping.return_value = {
            "id": "9847008",
            "conceptId": "9847008",
            "moduleId": "900000000000207008",
            "effectiveTime": "20020131",
            "definitionStatus": "PRIMITIVE",
            "idAndFsnTerm": "9847008 | structuur van hilum van bijnier",
            "active": True,
            "fsn": {
                "lang": "en",
                "term": "structuur van hilum van bijnier (lichaamsstructuur)"
            },
            "pt": {
                "lang": "en",
                "term": "structuur van hilum van bijnier"
            },
        }

        ecl_part = MappingECLPartFactory()
        concept = MappingECLConceptFactory(ecl=ecl_part, task=ecl_part.task, code="9847008", is_new=True)

        update_ecl_task(record_id=ecl_part.pk, query="test")
        self.assertEqual(ecl_part.concepts.count(), 1)

        concept.refresh_from_db()
        self.assertFalse(concept.is_new)

    @mock.patch("mapping.tasks.tasks.TerminiologieClient")
    def test_update_ecl_task_marking_concepts_as_deleted(self, term_client):
        term_client.return_value.expand_snomed_ecl_valueset.return_value = [
        ]

        ecl_part = MappingECLPartFactory()
        concept = MappingECLConceptFactory(ecl=ecl_part, task=ecl_part.task)
        self.assertEqual(ecl_part.concepts.count(), 1)

        update_ecl_task(record_id=ecl_part.pk, query="test")
        concept.refresh_from_db()
        self.assertTrue(concept.is_deleted)


    @mock.patch("mapping.tasks.tasks.TerminiologieClient")
    def test_update_ecl_task_removing_marked_for_deletion_concepts(self, term_client):
        term_client.return_value.expand_snomed_ecl_valueset.return_value = [
        ]

        ecl_part = MappingECLPartFactory()
        MappingECLConceptFactory(ecl=ecl_part, task=ecl_part.task, is_deleted=True)
        self.assertEqual(ecl_part.concepts.count(), 1)
        update_ecl_task(record_id=ecl_part.pk, query="test")
        self.assertEqual(ecl_part.concepts.count(), 0)
