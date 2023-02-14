from django.shortcuts import render

# Create your views here.

# howdy/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.template.defaultfilters import linebreaksbr
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from urllib.request import urlopen, Request
import urllib.parse
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.db.models import Q
from django.db.models.functions import Trunc, TruncMonth, TruncYear, TruncDay
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db.models import Max
import json
from validation.forms import *
from validation.models import *
from mapping.models import *
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
from validation.tasks import *
import time
import environ
import pandas as pd

from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response
from rest_framework import permissions 

# Import environment variables
env = environ.Env(DEBUG=(bool, False))
# reading .env file
environ.Env.read_env(env.str('ENV_PATH', '.env'))

class Permission_Validation_access(permissions.BasePermission):
    """
    Global permission check - rights to the translation validation module
    """
    def has_permission(self, request, view):
        if 'validation | access' in request.user.groups.values_list('name', flat=True):
            return True

# Return all users for admin purposes
class all_users(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def list(self, request):
  
        users = User.objects.all()

        output = []
        for user in users:
            output.append({
                'id' : user.id,
                'username' : user.username,
            })

        context = output
        return Response(context)

# Return tasks per user
class user_stats(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def list(self, request):
  
        users = User.objects.all()

        output = []
        for user in users:
            # Fetch tasks for user
            tasks = Task.objects.filter(access = user)
            if tasks.count() > 0:
                output.append({
                    'id' : user.id,
                    'username' : user.username,
                    'task_count' : tasks.count(),
                    'task_ids' : tasks.values('data__sortIndex')
                })

        context = output
        return Response(context)
