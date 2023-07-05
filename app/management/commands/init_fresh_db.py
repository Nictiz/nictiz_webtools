from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User


GROUPS = [
 'ATC lookup',                      # Access to the medication ATC/g-standaard lookup module
 'HTML tree',                       # Access to the Snomed list generators
 'mapping | access',                # Access to the mapping tool - not in use
 'mapping | edit mapping',          # Edit mappings, this enables changing and adding mappings
 'mapping | view tasks',            # View tasks in projects
 'mapping | create tasks',          # Create tasks through CSV entry
 'mapping | change task status',    
 'mapping | place comments',        
 'mapping | admin codesystems',     # Creating codesystems, loading data into codesystems
 'mapping | audit',                 # Create audit reports on mapping rules
 'mapping | project statistics',    # Show in-depth project statistics on project page
]

class Command(BaseCommand):
    help = 'Create base groups in fresh DB'

    def handle(self, *args, **options):
        groups = []
        for group_name in GROUPS:
            group, _ = Group.objects.get_or_create(name=group_name)
            groups.append(group)

        for user in User.objects.all():
            user.groups.add(*groups)