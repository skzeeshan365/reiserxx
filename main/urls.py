from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('open/<slug:post_slug>/', views.open_post, name='open'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('tag/<slug:tag_slug>/', views.search_by_tag, name='search_by_tag'),
    path('category/', views.categories, name='category'),
    path('category/<slug:category_slug>/', views.search_by_category, name='search_by_category'),
]
