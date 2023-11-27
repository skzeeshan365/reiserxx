from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='message_home'),
    path('mail/', views.mail, name='message_mail'),
]
