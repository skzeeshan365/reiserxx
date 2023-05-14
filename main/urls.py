from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
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
    path('<str:user>/<slug:post_slug>/', views.open_post, name='open'),
    path('<str:username>/', views.search_by_author, name='search_by_author'),
]
