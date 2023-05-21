from django.conf.urls.static import static
from django.urls import path, re_path

from djangoProject1 import settings
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('loadmore', views.load_more_posts, name='load_more'),
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
    re_path(r'^(?P<user>[^/]+)/(?P<post_slug>[^/]+)/$', views.open_post, name='open'),
    re_path(r'^(?P<username>[a-zA-Z0-9]{3,})/$', views.search_by_author, name='search_by_author')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
