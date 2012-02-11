from django.conf.urls.defaults import patterns

urlpatterns = patterns('myproject.tests',
    (r'^popup/$', 'views.popup'),
    (r'^pymorphy/$', 'views.pymorphy'),
)

