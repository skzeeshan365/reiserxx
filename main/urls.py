from django.conf.urls.static import static
from django.urls import path, re_path
from django.views.generic import RedirectView

from djangoProject1 import settings
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('loadmore/', views.load_more_posts, name='load_more'),
    path('loadtags/', views.load_tags, name='load_tags'),
    path('loadcategories/', views.load_categories, name='load_categories'),

    path('model/generation/image/', views.stable_diffusion, name='stable_diffusion'),
    path('model/generation/tags/', views.tag_generation, name='tag_generation'),
    path('model/summarization/summarize/', views.summarize_text, name='summary_generation'),

    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('lang/', views.lang, name='lang'),
    path('subscribe/verify/<str:subscriber_id>/', views.verify_email, name='verify_email'),
    path('search/', views.search, name='search'),
    path('tag/<slug:tag_slug>/', views.search_by_tag, name='search_by_tag'),
    path('category/', views.categories, name='category'),
    path('category/<slug:category_slug>/', views.search_by_category, name='search_by_category'),
    path('translate/<str:user>/<slug:post_slug>/<str:code>/', views.translate_post, name='translate'),
    path('privacypolicy/', views.policy, name='policy'),
    re_path(r'^(?P<user>[^/]+)/(?P<post_slug>[^/]+)/$', views.open_post, name='open'),
    re_path(r'^(?P<username>[a-zA-Z0-9]{3,})/$', views.search_by_author, name='search_by_author'),

    # Favicons
    path('android-icon-36x36.png', RedirectView.as_view(url=settings.STATIC_URL + 'reiserx/img/favicons/android-icon-36x36.png', permanent=True)),
    path('android-icon-48x48.png', RedirectView.as_view(url=settings.STATIC_URL + 'reiserx/img/favicons/android-icon-48x48.png', permanent=True)),
    path('android-icon-72x72.png', RedirectView.as_view(url=settings.STATIC_URL + 'reiserx/img/favicons/android-icon-72x72.png', permanent=True)),
    path('android-icon-96x96.png', RedirectView.as_view(url=settings.STATIC_URL + 'reiserx/img/favicons/android-icon-96x96.png', permanent=True)),
    path('android-icon-144x144.png', RedirectView.as_view(url=settings.STATIC_URL + 'reiserx/img/favicons/android-icon-144x144.png', permanent=True)),
    path('android-icon-192x192.png', RedirectView.as_view(url=settings.STATIC_URL + 'reiserx/img/favicons/android-icon-192x192.png', permanent=True)),
    path('android-icon-192x192.png', RedirectView.as_view(url=settings.STATIC_URL + 'reiserx/img/favicons/browserconfig.xml', permanent=True)),
    # Favicons



] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
