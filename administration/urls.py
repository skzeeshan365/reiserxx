from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('preview/', views.post_preview, name='post_preview'),
    path('home/', login_required(user_passes_test(lambda u: u.is_superuser)(views.post_create_view)), name='post_new'),
    path('login', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('category/', login_required(user_passes_test(lambda u: u.is_superuser)(views.category)), name='categories'),
    path('post/list/', login_required(user_passes_test(lambda u: u.is_superuser)(views.post_list)), name='post_list'),
    path('post/edit/<slug:post_slug>/', login_required(user_passes_test(lambda u: u.is_superuser)(views.post_edit)), name='post_edit'),
    path('post/delete/<slug:post_slug>/', login_required(user_passes_test(lambda u: u.is_superuser)(views.post_delete)), name='post_delete'),
]