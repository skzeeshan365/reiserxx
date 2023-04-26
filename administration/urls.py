from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='logs'),
    path('login', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('data/<int:pk>/', views.logview, name='data'),
    path('delete/<int:pk>/', views.delete, name='delete'),
    path('contacts', views.contacts, name='contacts'),
]