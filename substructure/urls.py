from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('bitstructures.substructure.views',
    (r'^$', 'blog'),
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[a-z0-9-]+)$', 'entry_page'),
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[a-z0-9-]+)/(?P<num>\d+)/(?P<filename>[a-zA-Z0-9-_\.]+)$', 'entry_codeblock'),
    (r'^drafts/(?P<slug>[a-z0-9-]+)$', 'draft_page'),
    (r'^drafts/(?P<slug>[a-z0-9-]+)/(?P<num>\d+)/(?P<filename>[a-zA-Z0-9-_\.]+)$', 'draft_codeblock'),
    (r'^fb-atom.xml$', 'atom_feed'),
    (r'^all$', 'all'),
    (r'^tagged-with/(?P<tag_name>[a-z0-9-]+)$', 'tagged_with'),
    (r'^robots.txt$', 'robots_txt')
)

if hasattr(settings, 'SUBSTRUCTURE_FEEDBURNER_REDIRECT_URL'):
    urlpatterns += patterns('',
        (r'^atom.xml$', 'bitstructures.substructure.views.redirect_to_feedburner'))
else:
    urlpatterns += patterns('',
        (r'^atom.xml$', 'bitstructures.substructure.views.atom_feed'))
