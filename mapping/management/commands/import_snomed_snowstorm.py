import requests
import os
from django.core.management.base import BaseCommand

from mapping.tasks.tasks import import_snomed_snowstorm
from terminologieserver.client import TerminiologieClient


class Command(BaseCommand):
    help = "Create base groups in fresh DB"

    def fetch_headers(self, username, password):
        data = {
            "grant_type": "password",
            "client_id": "cli_client",
            "username": username,
            "password": password,
        }
        token = requests.post(
            "https://terminologieserver.nl/auth/realms/nictiz/protocol/openid-connect/token",
            data=data,
        ).json()
        print(repr(token))
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token['access_token']}",
        }

    def handle(self, *args, **options):
        # result = import_snomed_snowstorm.apply()
        client = TerminiologieClient()
        client.login()

        data = client.expand_valueset()

        print("*" * 80)
        # 2print(repr(data))
        c = 0
        for x in data:
            c += 1
            print('.', end="")
        breakpoint()
