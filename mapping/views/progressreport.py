import json
import time
import urllib.parse
from urllib.request import Request, urlopen

import environ
from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView
from rest_framework import permissions, status, views, viewsets
from rest_framework.response import Response

from mapping.models import *
from mapping.tasks import *

# Import environment variables
env = environ.Env(DEBUG=(bool, False))
# reading .env file
environ.Env.read_env(env.str("ENV_PATH", ".env"))


class Permission_MappingTasks(permissions.BasePermission):
    """
    Global permission check rights to use the taskmanager.
    """

    def has_permission(self, request, view):
        if "mapping | audit" in request.user.groups.values_list("name", flat=True):
            return True


class Permission_Secret(permissions.BasePermission):
    """
    Global permission check rights to use the taskmanager.
    """

    def has_permission(self, request, view):
        if str(request.GET.get("secret")) != str(env("mapping_api_secret")):
            print("Incorrect or absent secret")
            return False
        else:
            return True


class progressReturnAll(viewsets.ViewSet):
    """
    Provides a list of all progress report items
    """

    permission_classes = [Permission_Secret]

    def retrieve(self, request, pk=None):
        print(
            f"[progressreport/progressReturnAll retrieve] requested by {request.user} - {pk}"
        )
        if pk == "status":
            records = MappingProgressRecord.objects.filter(name="TasksPerStatus")
            output = []
            for record in records:
                for value in json.loads(record.values):
                    output.append(
                        {
                            "project": str(record.project),
                            "status": value.get("status"),
                            "count": value.get("num_tasks"),
                            "time": record.time,
                        }
                    )
        elif pk == "user":
            records = MappingProgressRecord.objects.filter(name="TasksPerUser")
            output = []
            for record in records[0:100]:
                for value in json.loads(record.values):
                    output.append(value)
                    # output.append({
                    #     'project' : str(record.project),
                    #     'status' : value.get('status'),
                    #     'count' : value.get('num_tasks'),
                    #     'time' : record.time,
                    # })
        return Response(output)
