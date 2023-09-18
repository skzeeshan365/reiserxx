from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='payments_home'),
    path('config/', views.stripe_config, name='payment_config'),
    path('create-checkout-session/', views.create_checkout_session),
    path('success/', views.SuccessView.as_view()),
    path('cancelled/', views.CancelledView.as_view()),
    path('webhook/', views.stripe_webhook),
]
