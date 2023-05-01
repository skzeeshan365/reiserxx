from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('home/', login_required(user_passes_test(lambda u: u.is_superuser)(views.post_create_view)), name='post_new'),
    path('login', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('category/', login_required(user_passes_test(lambda u: u.is_superuser)(views.category)), name='categories'),
    path('post/', login_required(user_passes_test(lambda u: u.is_superuser)(views.post_edit)), name='post_edit'),
    path('robots.txt/', views.robots_txt, name='robots_txt'),
]