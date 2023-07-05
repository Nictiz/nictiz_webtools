from django.core.management.base import BaseCommand
from django.conf import settings

import pprint

from mapping.models import MappingEclPart
from mapping.tasks.tasks import UpdateECL1Task, update_ecl_task
from terminologieserver.client import TerminiologieClient


class Command(BaseCommand):
    help = "Create base groups in fresh DB"

    def handle(self, *args, **options):
        rec = MappingEclPart.objects.get(pk=29)
        # UpdateECL1Task(
        #     record_id=29,
        #     query="9847007 | Structure of hilum of adrenal gland (body structure) |"
        # )
        # rec.refresh_from_db()
        # print("*" * 80)
        # print(rec.result)

        mapping_record = update_ecl_task(
            record_id=29,
            query="9847007 | Structure of hilum of adrenal gland (body structure) |"
        )

        print("*" * 80)
        pprint.pprint(mapping_record.result)

        # client = TerminiologieClient(
        #     uri=settings.TERMINOLOGIE_URL,
        # )
        # client.login(
        #     username=settings.TERMINOLOGIE_USERNAME,
        #     password=settings.TERMINOLOGIE_PASSWORD,
        # )

        # expanded = self.get_expanded(
        #     client=client,
        #     ecl_query="9847007 | Structure of hilum of adrenal gland (body structure) |",
        # )

        # pprint.pprint(expanded)

        # for code in expanded["expansion"].get("contains", []):
        #     params = self.get_params(
        #         client=client, code=code["code"], system=code["system"]
        #     )
        #     pprint.pprint(params)

        #     pprint.pprint(client.params_to_dict(params))

        # breakpoint()

    def get_expanded(self, client, ecl_query):
        """Get result of expanded ecl query."""
        expanded = {
            "copyright": "This value set includes content from SNOMED CT, which is "
            "copyright © 2002+ International Health Terminology Standards "
            "Development Organisation (IHTSDO), and distributed by agreement "
            "between IHTSDO and HL7. Implementer use of SNOMED CT is not "
            "covered by this agreement",
            "expansion": {
                "contains": [
                    {
                        "code": "9847007",
                        "display": "structuur van hilum van bijnier",
                        "system": "http://snomed.info/sct",
                    }
                ],
                "extension": [
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/valueset-unclosed",
                        "valueBoolean": True,
                    }
                ],
                "identifier": "59d8ab3f-31db-4ce0-9b85-e32312fac54d",
                "offset": 0,
                "parameter": [
                    {
                        "name": "version",
                        "valueUri": "http://snomed.info/sct|http://snomed.info/sct/11000146104/version/20220930",
                    },
                    {"name": "count", "valueInteger": 2147483647},
                    {"name": "offset", "valueInteger": 0},
                ],
                "timestamp": "2023-02-22T09:44:36+01:00",
                "total": 1,
            },
            "experimental": False,
            "name": "SNOMED CT ECL expression",
            "resourceType": "ValueSet",
            "status": "active",
            "url": "http://snomed.info/sct/11000146104/version/20220930?fhir_vs=ecl%2F9847007+%7C+Structure+of+hilum+of+adrenal+gland+%28body+structure%29+%7C",
        }
        # expanded = client.expand_snomed_ecl_valueset(ecl_query=ecl_query)
        return expanded

    def get_params(self, client, code, system):
        """Get params by code and system."""
        params = [
            {"name": "name", "valueString": "module van Nederlandse editie"},
            {
                "name": "version",
                "valueString": "http://snomed.info/sct/11000146104/version/20220930",
            },
            {"name": "display", "valueString": "structuur van hilum van bijnier"},
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
            {
                "name": "property",
                "part": [
                    {"name": "code", "valueCode": "effectiveTime"},
                    {"name": "valueString", "valueString": "20020131"},
                ],
            },
            {
                "name": "property",
                "part": [
                    {"name": "code", "valueCode": "moduleId"},
                    {"name": "value", "valueCode": "900000000000207008"},
                ],
            },
            {
                "name": "designation",
                "part": [
                    {"name": "language", "valueCode": "en"},
                    {
                        "name": "use",
                        "valueCoding": {
                            "code": "900000000000013009",
                            "display": "Synonym",
                            "system": "http://snomed.info/sct",
                        },
                    },
                    {"name": "value", "valueString": "Hilum of adrenal gland"},
                ],
            },
            {
                "name": "designation",
                "part": [
                    {
                        "name": "language",
                        "valueCode": "en-x-sctlang-90000000-00005090-07",
                    },
                    {
                        "name": "use",
                        "valueCoding": {
                            "code": "preferredForLanguage",
                            "display": "Preferred For Language",
                            "system": "http://terminology.hl7.org/CodeSystem/hl7TermMaintInfra",
                        },
                    },
                    {
                        "name": "value",
                        "valueString": "Structure of hilum of adrenal gland",
                    },
                ],
            },
            {
                "name": "designation",
                "part": [
                    {
                        "name": "language",
                        "valueCode": "en-x-sctlang-90000000-00005080-04",
                    },
                    {
                        "name": "use",
                        "valueCoding": {
                            "code": "preferredForLanguage",
                            "display": "Preferred For Language",
                            "system": "http://terminology.hl7.org/CodeSystem/hl7TermMaintInfra",
                        },
                    },
                    {
                        "name": "value",
                        "valueString": "Structure of hilum of adrenal gland",
                    },
                ],
            },
            {
                "name": "designation",
                "part": [
                    {"name": "language", "valueCode": "en"},
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
                        "valueString": "Structure of hilum of adrenal gland (body "
                        "structure)",
                    },
                ],
            },
            {
                "name": "designation",
                "part": [
                    {"name": "language", "valueCode": "nl"},
                    {
                        "name": "use",
                        "valueCoding": {
                            "code": "900000000000013009",
                            "display": "Synonym",
                            "system": "http://snomed.info/sct",
                        },
                    },
                    {"name": "value", "valueString": "hilum glandulae suprarenalis"},
                ],
            },
            {
                "name": "designation",
                "part": [
                    {"name": "language", "valueCode": "nl"},
                    {
                        "name": "use",
                        "valueCoding": {
                            "code": "900000000000013009",
                            "display": "Synonym",
                            "system": "http://snomed.info/sct",
                        },
                    },
                    {"name": "value", "valueString": "hilum van bijnier"},
                ],
            },
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

        # params = client.lookup_code(code=code["code"], system=code["system"]).get("parameter", [])

        return params
