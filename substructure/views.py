from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, loader
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.conf import settings
from bitstructures.substructure.models import Entry, Tag, EntryTag
from bitstructures.substructure.codeblocks import MarkdownCodeblocksParser

DEFAULT_SUBSTRUCTURE_NUM_ENTRIES_PER_PAGE = 5

def blog(request):
    page = 1
    if ('page' in request.GET) and (int(request.GET['page']) > 0):
        page = int(request.GET['page'])
    if hasattr(settings, 'SUBSTRUCTURE_NUM_ENTRIES_PER_PAGE'):
        num_entries_per_page = settings.SUBSTRUCTURE_NUM_ENTRIES_PER_PAGE
    else:
        num_entries_per_page = DEFAULT_SUBSTRUCTURE_NUM_ENTRIES_PER_PAGE
    skip = (page - 1) * num_entries_per_page
    skip_to = skip + num_entries_per_page
    data = get_context_data(request)
    data['entry_list'] = get_published_entries().order_by('-date_published')[skip:skip_to]
    data['next_page'] = skip_to < data['num_published_entries']
    data['next_page_num'] = page + 1
    data['previous_page'] = page > 1
    data['previous_page_first_page'] = page == 2
    data['previous_page_num'] = page - 1
    return render_to_response('substructure/blog.html', data)

def entry_page(request, year, month, slug):
    entry = get_object_or_404(Entry, slug=slug)
    check_view_entry(entry, year, month)
    data = get_context_data(request)
    data['entry'] = entry
    return render_to_response('substructure/entry_page.html', data)

def entry_codeblock(request, year, month, slug, num, filename):
    entry = get_object_or_404(Entry, slug=slug)
    check_view_entry(entry, year, month)
    return get_codeblock_response(entry, num, filename)

def check_view_entry(entry, year, month):
    if not entry.is_published():
        raise Http404
    if int(year) != entry.date_published.year:
        raise Http404
    if int(month) != entry.date_published.month:
        raise Http404

def draft_page(request, slug):
    entry = get_object_or_404(Entry, slug=slug)
    check_view_draft(request, entry)
    data = get_context_data(request)
    data['entry'] = entry
    return render_to_response('substructure/entry_page.html', data)

def draft_codeblock(request, slug, num, filename):
    entry = get_object_or_404(Entry, slug=slug)
    check_view_draft(request, entry)
    return get_codeblock_response(entry, num, filename)

def check_view_draft(request, entry):
    if not entry.is_draft():
        raise Http404

def get_codeblock_response(entry, num, filename):
    parser = MarkdownCodeblocksParser()
    codeblock = parser.get_codeblock(entry.text, int(num))
    if codeblock:
        if filename.lower().endswith('html'):
            return HttpResponse(codeblock.get_code(), mimetype='text/html')
        else:
            return HttpResponse(codeblock.get_code(), mimetype='text/plain')
    else:
        raise Http404

def atom_feed(request):
    t = loader.get_template('substructure/atom_feed.xml')
    current_site = Site.objects.get_current()
    entry_list = Entry.objects.filter(date_published__isnull=False).order_by('-date_published')
    c = Context({
        'site_name': current_site.name,
        'site_domain': current_site.domain,
        'entry_list': entry_list
    })
    if len(entry_list) > 0:
        c['most_recent_date_published'] = entry_list[0].date_published
    return HttpResponse(t.render(c), mimetype='application/atom+xml')

def all(request):
    data = get_context_data(request)
    data['entry_list'] = get_published_entries().order_by('-date_published')
    return render_to_response('substructure/all.html', data)

def tagged_with(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    data = get_context_data(request)
    data['tag'] = tag
    entry_list = get_published_entries_with_tag(tag)
    entry_list.sort(key=get_entry_date_published,reverse=True)
    data['entry_list'] = entry_list
    return render_to_response('substructure/tagged-with.html', data)

def get_published_entries_with_tag(tag):
    entrytags = EntryTag.objects.select_related().filter(tag=tag)
    entry_list = []
    for entrytag in entrytags:
        entry = entrytag.entry
        if entry.is_published:
            entry_list.append(entry)
    return entry_list

def get_entry_date_published(entry):
    return entry.date_published

def robots_txt(request):
    return HttpResponse(render_to_string('substructure/robots.txt'),
        mimetype='text/plain')

def get_published_entries():
    return Entry.objects.filter(date_published__isnull=False)

def redirect_to_feedburner(request):
    return HttpResponseRedirect(settings.SUBSTRUCTURE_FEEDBURNER_REDIRECT_URL)

def get_context_data(request):
    data = { 'MEDIA_URL': settings.MEDIA_URL }
    data['num_published_entries'] = get_published_entries().count()
    return data
