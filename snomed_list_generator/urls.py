# build_tree/urls.py
from django.urls import path

from . import views

app_name = 'snomed_list'

urlpatterns = [
    path(r'download/<str:downloadfile>', views.DownloadFile.as_view(), name='download'),
    path(r'index/', views.createTaskPageView.as_view(), name='index'),
    path(r'create_task/', views.ajaxCreateTask.as_view(), name='create_task'),
    path(r'get_tasks/', views.showTaskPageView.as_view(), name='get_tasks'),
    path(r'', views.createTaskPageView.as_view()),
]
