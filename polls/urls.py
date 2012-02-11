from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('myproject.polls',
    (r'^$', 'views.index'),
    (r'^request/$', 'directrequest.request'),
    (r'^company/$', 'make_company.post'),
    (r'^gen_phrases/$', 'views.gen_phrases'),
)


