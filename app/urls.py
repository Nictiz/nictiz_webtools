"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# from django.urls import path, url
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'auth/', include('rest_framework.urls')),
    path(r'jwtauth/', include('jwtauth.urls'), name='jwtauth'),
    path(r'accounts/', include('django.contrib.auth.urls')),
    path(r'medicatie/', include('atc_lookup.urls')),
    path(r'build_tree_excel/', include('build_tree_excel.urls')),
    path(r'build_tree/', include('build_tree.urls')), 
    path(r'snomed_list/', include('snomed_list_generator.urls')), 
    path(r'mapping/', include('mapping.urls')), 
    path(r'epd/', include('epd.urls')), 
    path(r'termspace/', include('termspace.urls')), 
    path(r'dhd/', include('dhd.urls')), 
    path(r'postco/', include('postcoordination.urls')), 
    path(r'validation/', include('validation.urls')), 
    path(r'qa_service/', include('qa_service.urls')), 
    path(r'nts/', include('terminologieserver.urls')), 
    # url(r'^select2/', include('django_select2.urls')),
    path(r'', include('homepage.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns