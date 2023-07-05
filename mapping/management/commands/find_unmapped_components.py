from django.core.management.base import BaseCommand

from mapping.tasks.qa_unmapped_components import unmapped_components


class Command(BaseCommand):
    help = "Find list of unmapped mapping components."

    def handle(self, *args, **options):
        result = unmapped_components()

        print(result)
