"""djangoProject1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Primary
    2. Add a URL to urlpatterns:  path('', Primary.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import RedirectView

import administration.views
from main.sitemap import sitemaps, CategorySitemap, TagSitemap, PostSitemap
from main.sitemap_lang import DynamicSitemap
from main.views import dynamic_sitemap
from reiserx.sitemap import sitemaps as sitemap_system

urlpatterns = [
    path('administration/', admin.site.urls),
    path('admin/', include('administration.urls')),

    # Sitemaps
    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('sitemap-categories.xml/', sitemap, {'sitemaps': {'categories': CategorySitemap}}, name='category_sitemap'),
    path('sitemap-tags.xml/', sitemap, {'sitemaps': {'tags': TagSitemap}}, name='tag_sitemap'),
    path('sitemap-posts.xml/', sitemap, {'sitemaps': {'posts': PostSitemap}}, name='post_sitemap'),
    path('sitemap-reiserx-system.xml/', sitemap, {'sitemaps': sitemap_system}, name='system_sitemap'),
    path('sitemap-posts-<str:language>.xml/', dynamic_sitemap, name='dynamic_sitemap'),

    # robots.txt
    path('robots.txt/', administration.views.robots_txt, name='robots_txt'),

    # Reiser-System
    path('reiserx-system/', include('reiserx.urls')),

    path('ads.txt/', RedirectView.as_view(url=settings.STATIC_URL + 'Ads/ads.txt', permanent=True)),

    path('', include('main.urls')),
]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
