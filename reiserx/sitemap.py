from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    def items(self):
        return ['reiserx_home', 'Documentation']  # Add the names of your static views here

    def location(self, item):
        return reverse(item)


sitemaps = {
    'static': StaticViewSitemap,  # Add the new sitemap class here
}