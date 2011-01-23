from django.db import models

class Entry(models.Model):
    """
    >>> from datetime import datetime
    >>> test1 = Entry()
    >>> test1.id = 1
    >>> test1.slug = 'testentry1'
    >>> test1.is_published()
    False
    >>> test1.is_draft()
    True
    >>> test1.get_absolute_url()
    '/drafts/testentry1'
    >>> test2 = Entry()
    >>> test2.id = 2
    >>> test2.slug = 'testentry2'
    >>> test2.date_published = datetime(2001, 2, 3)
    >>> test2.is_published()
    True
    >>> test2.is_draft()
    False
    >>> test2.get_absolute_url()
    '/2001/02/testentry2'
    """

    slug = models.SlugField(unique=True, blank=False)
    title = models.CharField(maxlength=200, blank=False)
    date_published = models.DateTimeField(null=True, blank=True)
    text = models.TextField(blank=False)

    def __str__(self):
        return self.title

    def is_published(self):
        return bool(self.date_published)

    def is_draft(self):
        return not self.is_published()

    def get_absolute_url(self):
        if self.is_published():
            year = self.date_published.year
            month = self.date_published.month
            return '/%04d/%02d/%s' % (year, month, self.slug)
        else:
            return '/drafts/%s' % (self.slug)

    def tags(self):
        entrytags = EntryTag.objects.select_related().filter(entry=self).order_by('number')
        tags = []
        for entrytag in entrytags:
            tags.append(entrytag.tag)
        return tags

    class Admin:
        fields = (
            (None, {'fields': ('title', 'slug', 'date_published')}),
            (None, {'fields': ('text',), 'classes': 'monospace'})
        )
        list_display = ('title', 'get_absolute_url', 'date_published')
        ordering = ['-date_published']

class Tag(models.Model):
    name = models.CharField(maxlength=50, blank=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/tagged-with/%s' % (self.name)

    class Admin:
        pass

class EntryTag(models.Model):
    entry = models.ForeignKey(Entry)
    tag = models.ForeignKey(Tag)
    number = models.IntegerField()

    class Admin:
        list_display = ('entry', 'tag', 'number')
        ordering = ['entry']
