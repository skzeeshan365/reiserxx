from django.conf.urls.static import static
from django.urls import path, re_path
from django.views.generic import RedirectView

from djangoProject1 import settings
from . import views
from .feeds import BlogFeed

urlpatterns = [
    path('', views.home, name='home'),
    path('loadmore/', views.load_more_posts, name='load_more'),
    path('loadtags/', views.load_tags, name='load_tags'),
    path('loadcategories/', views.load_categories, name='load_categories'),

    # AI Models
    path('ai/generation/image/', views.stable_diffusion, name='stable_diffusion'),
    path('ai/generation/tags/', views.tag_generation, name='tag_generation'),
    path('ai/summarization/summarize/', views.summarize_text, name='summary_generation'),
    path('ai/api/summarization/summarize/', views.summarize_text_api, name='summary_generation_api'),
    path('ai/generation/text/', views.generation_gpt_neo_2_7_B, name='text_generation'),
    path('ai/transcription/whisper/', views.transcribe, name='transcription'),

    path('feed/rss/', BlogFeed(), name='rss_feed'),  # URL for RSS feed

    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('lang/', views.lang, name='lang'),
    path('subscribe/verify/<str:subscriber_id>/', views.verify_email, name='verify_email'),
    path('search/', views.search, name='search'),
    path('tag/<slug:tag_slug>/', views.search_by_tag, name='search_by_tag'),
    path('category/', views.categories, name='category'),
    path('category/<slug:category_slug>/', views.search_by_category, name='search_by_category'),
    path('privacy-policy/', views.policy, name='policy'),
    path('terms-of-service/', views.terms, name='terms_of_service'),
    path('refund-policy/', views.refund, name='refund_policy'),

    path('share/<str:short_slug>/', views.open_shared_post, name='open_shared'),

    path('languages/', views.lang_page, name='lang_page'),
    path('languages/<str:code>/', views.lang_posts_page, name='lang_posts_page'),
    path('api/languages/<str:code>/', views.load_lang_posts, name='load_lang_posts'),

    path('<str:user>/<slug:post_slug>/<str:code>/', views.translate_post, name='translate'),

    path('comment_reply/<int:comment_id>/', views.post_reply, name='post_reply'),
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

    path('screenshot-privacy-policy', views.screenshot_policy, name='screenshot_policy'),

    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
