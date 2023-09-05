from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from main.models import Post


class DynamicSitemap(Sitemap):
    priority = 1.0

    def __init__(self, language):
        self.language = language

    def items(self):
        return Post.objects.filter(draft=False).values('author__username', 'slug', 'timestamp').order_by('-timestamp')

    def location(self, post):
        return reverse("translate", args=[post['author__username'], post['slug'], self.language])

    def lastmod(self, post):
        return post['timestamp']