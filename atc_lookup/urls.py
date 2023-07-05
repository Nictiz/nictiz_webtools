# howdy/urls.py
from django.urls import path

from . import views

app_name = 'atc_lookup'
urlpatterns = [
    #url(r'medicatie/', views.get_name, name='medicatie'),
    path(r'index/', views.MedicinPageView.as_view(), name='index'),
]
