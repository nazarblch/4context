from django.conf.urls.defaults import patterns, include, url
from django.conf import settings



from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('myproject.project',

    (r'^$', 'views.index'),
    (r'^sort_kw_phr/$', 'views.sort_kw_phr'),
    (r'^keywords/$', 'views.keyword'),

)



