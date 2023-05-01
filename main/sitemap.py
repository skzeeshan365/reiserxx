from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Category, Post, Tag


class CategorySitemap(Sitemap):
    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('search_by_category', args=[obj.slug])


class TagSitemap(Sitemap):
    def items(self):
        return Tag.objects.all()

    def location(self, obj):
        return reverse('search_by_tag', args=[obj.slug])


class PostSitemap(Sitemap):
    def items(self):
        return Post.objects.order_by('-id')

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.timestamp


class StaticViewSitemap(Sitemap):
    def items(self):
        return ['home', 'about', 'search', 'category']  # Add the names of your static views here

    def location(self, item):
        return reverse(item)


sitemaps = {
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'posts': PostSitemap,
    'static': StaticViewSitemap,  # Add the new sitemap class here
}