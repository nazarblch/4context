from django.conf.urls.defaults import patterns, include, url
from django.conf import settings


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^polls/', include('myproject.polls.urls')),
    url(r'^shop/', include('myproject.shop.urls')),
	
    url(r'^project/', include('myproject.project.urls')),
    
    url(r'^agency/', include('myproject.agency.urls')),

    url(r'^tests/', include('myproject.tests.urls')),
  
    
)

'''
urlpatterns += patterns('',
           (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'./media/'}),
)

'''

urlpatterns+=patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve',  
         	{'document_root':     settings.MEDIA_ROOT}),

)

