from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Category, Post, Tag


class CategorySitemap(Sitemap):
    priority = 0.8

    def items(self):
        return Category.objects.order_by('-id')

    def location(self, obj):
        return reverse('search_by_category', args=[obj.slug])


class TagSitemap(Sitemap):
    priority = 0.3

    def items(self):
        return Tag.objects.order_by('-id')

    def location(self, obj):
        if obj.slug:
            return reverse('search_by_tag', args=[obj.slug])
        else:
            return None


class PostSitemap(Sitemap):
    priority = 1.0

    def items(self):
        return Post.objects.order_by('-id')

    def location(self, obj):
        return reverse('open', kwargs={'user': obj.author.username, 'post_slug': obj.slug})

    def lastmod(self, obj):
        return obj.timestamp


class StaticViewSitemap(Sitemap):
    def items(self):
        return ['home', 'contact', 'search', 'category', 'about', 'subscribe', 'policy', 'stable_diffusion', 'tag_generation', 'summary_generation', 'text_generation']  # Add the names of your static views here

    def location(self, item):
        return reverse(item)


sitemaps = {
    'static': StaticViewSitemap,  # Add the new sitemap class here
}