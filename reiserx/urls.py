from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('privacypolicy/', views.policy, name="policy"),
    path('reiserxprivacypolicy/', views.reiserxpolicy, name="ReiserX privacy policy"),
    path('terms of use/', views.terms, name="terms of use"),
    path('contact', views.contact, name="contact"),
    path('Documentation/', views.setupguide, name="Documentation"),
    path('media/<int:pk>/', views.media, name="media"),
]
