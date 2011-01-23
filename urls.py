from django.conf.urls.defaults import *
import bitstructures.substructure.urls

urlpatterns = patterns('',
    (r'^$', include('bitstructures.substructure.urls')),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^css/(.*)$', 'django.views.static.serve', {'document_root': 'css'}),
    (r'^images/(.*)$', 'django.views.static.serve', {'document_root': 'images'}),
)

urlpatterns += bitstructures.substructure.urls.urlpatterns
