from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
import sys, os

from requests.sessions import extract_cookies_to_jar
import environ
import time
import random
import json
import urllib.request
import re
import uuid

from rest_framework import viewsets
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework import permissions

from mapping.tasks import *
from mapping.models import *

# Import environment variables
env = environ.Env(DEBUG=(bool, False))
# reading .env file
environ.Env.read_env(env.str('ENV_PATH', '.env'))

from snowstorm_client import Snowstorm

class Permission_MappingProject_Access(permissions.BasePermission):
    """
    Global permission check rights to use the RC Audit functionality.
    """
    def has_permission(self, request, view):
        if 'mapping | access' in request.user.groups.values_list('name', flat=True):
            return True

class Permission_MappingProject_ChangeMappings(permissions.BasePermission):
    """
    Global permission check rights to change mappings.
    """
    def has_permission(self, request, view):
        if 'mapping | edit mapping' in request.user.groups.values_list('name', flat=True):
            return True

class ExportEclSourceData(viewsets.ViewSet):
    """
    Outputs the source data of ECL-1 projects, for reproduction of the project in another system
    """

    permission_classes = [Permission_MappingProject_ChangeMappings]

    def retrieve(self, request, pk=None):
        
        try:
            project = MappingProject.objects.get(id=pk)
            if project.project_type != '4':
                raise Exception("Not an ECL-1 project.")
        except Exception as e:
            return Response(f"Probleem bij selecteren project. Bestaat het ID {pk}? Error: {e}")

        # Fetch tasks
        filtered_tasks = MappingTask.objects.order_by('id').filter(project_id = project).prefetch_related(
            'source_component',
            'source_component__codesystem_id',
            'user',
            'status',
            )

        # Fetch exclusions
        exclusions = MappingEclPartExclusion.objects.all().values(
            'task__id', 
            'components'
            )
        exclusions = {
                int(item['task__id']) : item['components'] 
                for item in exclusions if item['components']!=[""]
            }


        # Fetch all ECL queries
        ecl_parts = MappingEclPart.objects.filter(task__project_id = project).values(
            'task__id',
            'query',
            'mapcorrelation',
            'description',
        )
        ecl_parts = [{
                        'task__id' : int(item['task__id']),
                        'query': item['query'],
                        'correlation' : item['mapcorrelation'],
                        'description' : item['description']
                    }
                for item in ecl_parts]

        # Fetch all comments
        comments = MappingComment.objects.filter(comment_task__project_id = project).prefetch_related(
            'user',
            'task'
        ).values(
            'comment_task__id',
            'comment_body',
            'comment_user__username',
            'comment_created',
        )
        comments = [{
                        'task__id' : int(item['comment_task__id']),
                        'body': item['comment_body'],
                        'user' : item['comment_user__username'],
                        'created' : item['comment_created']
                    }
                for item in comments]

        # Fetch all QA hits
        qa_hits = MappingTaskAudit.objects.filter(task__project_id = project).prefetch_related(
            'user',
            'task'
        ).values(
            'task__id',
            'audit_type',
            'hit_reason',
            'sticky',
            'ignore',
            'ignore_user',
        )
        qa_hits = [{
                        'task__id' : int(item['task__id']),
                        'audit_type': item['audit_type'],
                        'hit_reason' : item['hit_reason'],
                        'sticky' : item['sticky'],
                        'whitelisted' : item['ignore'],
                        'whitelisted_by_user' : item['ignore_user'],
                    }
                for item in qa_hits]

        # Loop over tasks
        tasks = [{
                'id' : task.id,
                'category' : task.category,
                'target' : {
                    'code' : task.source_component.component_id,
                    'codesystem' : {
                        'title' : task.source_component.codesystem_id.codesystem_title,
                        'fhir_uri' : task.source_component.codesystem_id.codesystem_fhir_uri,
                        'id' : task.source_component.codesystem_id.id,
                        'version' : task.source_component.codesystem_id.codesystem_version,
                    },
                    'title' : task.source_component.component_title,
                },
                'status' : {
                    'id' : task.status.id,
                    'title' : task.status.status_title,
                },
                'exclusions' : exclusions.get(task.id,[]),
                'ecl_queries' : list(filter(lambda item: (item['task__id'] == task.id), ecl_parts)),
                'comments' : list(filter(lambda item: (item['task__id'] == task.id), comments)),
                'qa_hits' : list(filter(lambda item: (item['task__id'] == task.id), qa_hits)),
            } for task in filtered_tasks]
        
        output = {
            'project' : {
                'id' : project.id,
                'title' : project.title,
            },
            'tasks' : tasks
        }


        return Response(output)
