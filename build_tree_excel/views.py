from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Sum
from .forms import *
from django.contrib.auth.mixins import  UserPassesTestMixin
from .build_tree import *
from .models import taskRecordBuildFlat
from .tasks import *
import glob
import os
from django.shortcuts import redirect
from django.urls import reverse


# Create your views here.
class DownloadFile(UserPassesTestMixin, TemplateView):
    def handle_no_permission(self):
        return redirect('login')
    def test_func(self):
        #return self.request.user.has_perm('Build_Tree.make_taskRecordBuildFlat')
        return self.request.user.groups.filter(name='HTML tree').exists()
    
    def get(self, request, **kwargs):
        username = None
        if request.user.is_active:
            username = request.user.username
        else:
            username = "NULL"

        template_name = 'build_tree_excel/index.html'

        context = super(DownloadFile, self).get_context_data(**kwargs)
        downloadfileId = int(kwargs.get('downloadfile'))
        taskData = taskRecordBuildFlat.objects.filter(username=username, id=downloadfileId, output_available=True).values()
        #print(taskData[0]['filename'])

        #filename = os.path.dirname(os.path.abspath(__file__))+"/static_files/output/{}".format(taskData[0]['filename'])
        filename = "/webserver/static_files/tree/{}".format(taskData[0]['filename'])
        response = HttpResponse(open(filename, 'rb').read())
        response['Content-Type'] = 'text/plain'
        response['Content-Disposition'] = 'attachment; filename=SnomedTree-{}.xlsx'.format(taskData[0]['conceptFSN'].replace(" ", "_"))

        # Set file as not available in database and delete html file
        obj = taskRecordBuildFlat.objects.get(id=downloadfileId)
        obj.output_available = False
        obj.save()

        os.remove(filename)
        return response


class BuildTreeView(UserPassesTestMixin, TemplateView):
    def handle_no_permission(self):
        return redirect('login')
    def test_func(self):
        #return self.request.user.has_perm('Build_Tree.make_taskRecordBuildFlat')
        return self.request.user.groups.filter(name='HTML tree').exists()
    
    # Handle POST data if present
    def post(self, request, **kwargs):
        if request.method == 'POST':
            # check whether it's valid:
            username = None
            if request.user.is_active:
                username = request.user.username
            else:
                username = "NULL"

            form = SearchForm(request.POST)
            if form.is_valid():
                sctid = str(form.cleaned_data['searchterm'])

                # Get task.id for tracking purposes
                task = build_flat_tree_async.delay(sctid, username)
                task_id = task.id

                return HttpResponseRedirect(reverse('build_tree_excel:index'))

    # if a GET (or any other method) create a blank form
    def get(self, request, **kwargs):
        username = None
        if request.user.is_active:
            username = request.user.username
        else:
            username = "NULL"
        form = SearchForm()
        # Ophalen bestaande taken overnemen van hier boven
        # tasksPerUser = taskRecordBuildFlat.objects.all().order_by("-timestamp")
        totalRunTime = taskRecordBuildFlat.objects.aggregate(Sum('execution_time'))
        try:
            totalRunTime = round(totalRunTime['execution_time__sum'])
        except:
            totalRunTime = "error"
        tasksPerUser = taskRecordBuildFlat.objects.filter(username=username).order_by("-timestamp")
        return render(request, 'build_tree_excel/index.html', {
            'page_title': 'Boomstructuur HTML',
            'form': form,
            'tasksPerUser': tasksPerUser,
            'totalRunTime': totalRunTime,
        })

class TermspaceQaDownload(UserPassesTestMixin, TemplateView):
    def handle_no_permission(self):
        return redirect('login')
    def test_func(self):
        #return self.request.user.has_perm('Build_Tree.make_taskRecordBuildFlat')
        return self.request.user.groups.filter(name='HTML tree').exists()
    
    def get(self, request, **kwargs):
        downloadfileName = str(kwargs.get('downloadfile'))
        filename = "/webserver/static_files/termspace_qa/{}.xlsx".format(downloadfileName)
        response = HttpResponse(open(filename, 'rb').read())
        response['Content-Type'] = 'text/plain'
        response['Content-Disposition'] = 'attachment; filename=termspace-QA-{}.xlsx'.format(downloadfileName)

        os.remove(filename)
        return response

class TermspaceQaOverview(UserPassesTestMixin, TemplateView):
    def handle_no_permission(self):
        return redirect('login')
    def test_func(self):
        #return self.request.user.has_perm('Build_Tree.make_taskRecordBuildFlat')
        return self.request.user.groups.filter(name='HTML tree').exists() # TODO
    
    # Handle POST data if present
    def post(self, request, **kwargs):
        if request.method == 'POST':
            form = QaForm(request.POST)
            if form.is_valid():
                tasklist = str(form.cleaned_data['concepts'])

                # Get task.id for tracking purposes
                task = termspace_audit.delay(tasklist)
                task_id = task.id

                return HttpResponseRedirect(reverse('build_tree_excel:qa_index'))

    # if a GET (or any other method) create a blank form
    def get(self, request, **kwargs):
        
        form = QaForm()

        files = glob.glob('/webserver/static_files/termspace_qa/*')
        file_list = []
        for file in files:
            file_list.append(str(file).split("/")[-1])

        return render(request, 'build_tree_excel/termspace_qa_list/index.html', {
            'page_title': 'Termspace QA',
            'form': form,
            'files' : list(reversed(file_list)),
        })
