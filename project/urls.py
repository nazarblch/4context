from django.conf.urls.defaults import patterns, include, url
from django.conf import settings


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('myproject.project',
        (r'^', 'views.index'),               
        (r'^create_company/', 'views.create_company'),  
)



