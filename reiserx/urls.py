from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='reiserx_home'),
    path('privacy-policy/', views.policy, name="policy"),
    path('reiserx-privacy-policy/', views.reiserxpolicy, name="ReiserX privacy policy"),
    path('terms of use/', views.terms, name="terms of use"),
    path('contact', views.contact, name="reiserx_contact"),
    path('Documentation/', views.setupguide, name="Documentation"),
    path('media/<int:pk>/', views.media, name="media"),
    path('changelogs/', views.changelogs, name="changelogs"),
    path('portfolio/', views.portfolio, name="portfolio"),
]
