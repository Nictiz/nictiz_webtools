# howdy/urls.py
from django.urls import path

from . import views

app_name = 'epd'
urlpatterns = [
    #url(r'medicatie/', views.get_name, name='medicatie'),
    path(r'test', views.api_ApiTest_get.as_view(), name='test'),

    path(r'decursus/<int:patientid>/<int:decursusId>', views.api_decursus.as_view(), name='decursus-detail'),
    path(r'decursus/<int:patientid>', views.api_decursus.as_view(), name='decursus-list'),
    path(r'decursus', views.api_decursus.as_view(), name='decursus'),

    path(r'problem', views.api_problem.as_view(), name='problem'),

    path(r'patient/<int:id>', views.api_patient_get.as_view(), name='patient-detail'),
    path(r'patient', views.api_patient_get.as_view(), name='patient-list'),
]
