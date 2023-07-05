import time

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions


class Permission_Validation_access(permissions.BasePermission):
    """
    Global permission check - rights to the translation validation module
    """
    def has_permission(self, request, view):
        if 'validation | access' in request.user.groups.values_list('name', flat=True):
            return True

# Search termspace comments
class test_api(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    def list(self, request):
        from qa_service.tasks.test_suite import run_testsuite
        start = time.time()
        result = run_testsuite.delay()

        while result.status != 'SUCCESS':
            time.sleep(1)

        return Response({
            'message' : 'QA wordt uitgevoerd. Resultaat in console log, of uiteindelijk de webhook.',
            'tests' : result.result,
            'Runtime (seconden)' : int(time.time()-start),
        })
