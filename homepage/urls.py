# howdy/urls.py
from django.urls import path

from . import views

app_name = 'homepage'
urlpatterns = [
    path(r'', views.HomePageView.as_view(), name='index'),
]
