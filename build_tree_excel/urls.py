# build_tree/urls.py
from django.urls import path

from . import views

app_name = 'build_tree_excel'

urlpatterns = [
    path(r'qa/download/<str:downloadfile>', views.TermspaceQaDownload.as_view(), name='qa_download'),
    path(r'qa/', views.TermspaceQaOverview.as_view(), name='qa_index'),
    path(r'download/<str:downloadfile>', views.DownloadFile.as_view(), name='download'),
    path(r'index/', views.BuildTreeView.as_view(), name='index'),
    path(r'', views.BuildTreeView.as_view()),
]
