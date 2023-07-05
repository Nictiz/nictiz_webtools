# build_tree/urls.py
from django.urls import path

from . import views

app_name = 'build_tree'

urlpatterns = [
    path(r'download/<str:downloadfile>', views.DownloadFile.as_view(), name='download'),
    path(r'index/', views.BuildTreeView.as_view(), name='index'),
    path(r'', views.BuildTreeView.as_view()),
]
