from django.test import TestCase

from terminologieserver.client import TerminiologieClient, TerminologieRequestError


class TerminologieClientTestCase(TestCase):
    def test_params_to_dict_raw_properties(self):
        """Test params_to_dict functionality.

        Confirm that raw properties are in result.
        """

        params = [
            {"name": "name", "valueString": "module van Nederlandse editie"},
            {
                "name": "version",
                "valueString": "http://snomed.info/sct/11000146104/version/20220930",
            },
            {"name": "display", "valueString": "structuur van hilum van bijnier"},
        ]
        result = TerminiologieClient.params_to_dict(params=params)

        self.assertEqual(
            result,
            {
                "display": "structuur van hilum van bijnier",
                "version": "http://snomed.info/sct/11000146104/version/20220930",
                "name": "module van Nederlandse editie",
            },
        )

    def test_params_to_dict_properties(self):
        """Test params_to_dict functionality.

        Confirm that properties returned as flat dictionary.
        """

        params = [
            {
                "name": "property",
                "part": [
                    {"name": "code", "valueCode": "parent"},
                    {"name": "value", "valueCode": "362894002"},
                ],
            },
            {
                "name": "property",
                "part": [
                    {"name": "code", "valueCode": "child"},
                    {"name": "value", "valueCode": "249332001"},
                ],
            },
            {
                "name": "property",
                "part": [
                    {"name": "code", "valueCode": "sufficientlyDefined"},
                    {"name": "valueBoolean", "valueBoolean": False},
                ],
            },
        ]

        result = TerminiologieClient.params_to_dict(params=params)

        self.assertEqual(
            result,
            {
                "parent": "362894002",
                "child": "249332001",
                "sufficientlyDefined": False,
            },
        )

    def test_params_to_dict_designations(self):
        """Test params_to_dict functionality.

        Confirm that designations returned as flat dictionary.
        """

        params = [
            {
                "name": "designation",
                "part": [
                    {"name": "language", "valueCode": "en"},
                    {
                        "name": "use",
                        "valueCoding": {
                            "code": "display",
                            "system": "http://terminology.hl7.org/CodeSystem/designation-usage",
                        },
                    },
                    {"name": "value", "valueString": "structuur van hilum van bijnier"},
                ],
            },
            {
                "name": "designation",
                "part": [
                    {"name": "language", "valueCode": "nl-x-sctlang-31000146-106"},
                    {
                        "name": "use",
                        "valueCoding": {
                            "code": "preferredForLanguage",
                            "display": "Preferred For Language",
                            "system": "http://terminology.hl7.org/CodeSystem/hl7TermMaintInfra",
                        },
                    },
                    {"name": "value", "valueString": "structuur van hilum van bijnier"},
                ],
            },
            {
                "name": "designation",
                "part": [
                    {"name": "language", "valueCode": "nl"},
                    {
                        "name": "use",
                        "valueCoding": {
                            "code": "900000000000003001",
                            "display": "Fully specified name",
                            "system": "http://snomed.info/sct",
                        },
                    },
                    {
                        "name": "value",
                        "valueString": "structuur van hilum van bijnier "
                        "(lichaamsstructuur)",
                    },
                ],
            },
        ]

        result = TerminiologieClient.params_to_dict(params=params)

        self.assertEqual(
            result,
            {
                "nl:900000000000003001": "structuur van hilum van bijnier (lichaamsstructuur)",
                "nl:preferredForLanguage": "structuur van hilum van bijnier",
                "en:display": "structuur van hilum van bijnier",
            },
        )

    def test_expanded_data_to_snowstorm_mapping(self):
        data = {
            "code": "9847007",
            "display": "structuur van hilum van bijnier",
            "system": "http://snomed.info/sct",
            "name": "module van Nederlandse editie",
            "version": "http://snomed.info/sct/11000146104/version/20220930",
            "en:900000000000013009": "Hilum of adrenal gland",
            "en:preferredForLanguage": "Structure of hilum of adrenal gland",
            "en:900000000000003001": "Structure of hilum of adrenal gland (body structure)",
            "nl:900000000000013009": "hilum van bijnier",
            "en:display": "structuur van hilum van bijnier",
            "nl:preferredForLanguage": "structuur van hilum van bijnier",
            "nl:900000000000003001": "structuur van hilum van bijnier (lichaamsstructuur)",
            "parent": "362894002",
            "child": "249332001",
            "sufficientlyDefined": False,
            "effectiveTime": "20020131",
            "moduleId": "900000000000207008",
        }

        result = TerminiologieClient.expanded_data_to_snowstorm_mapping(
            expanded_data=data
        )

        self.assertEqual(
            result,
            {
                "id": "9847007",
                "pt": {"lang": "en", "term": "Structure of hilum of adrenal gland"},
                "fsn": {
                    "lang": "en",
                    "term": "Structure of hilum of adrenal gland (body structure)",
                },
                "active": True,
                "moduleId": "900000000000207008",
                "conceptId": "9847007",
                "idAndFsnTerm": "9847007 | Structure of hilum of adrenal gland (body structure) |",
                "effectiveTime": "20020131",
                "definitionStatus": "PRIMITIVE",
            },
        )
