from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('esewa/pay/<str:order_number>/', views.initiate_esewa, name='initiate_esewa'),
    path('esewa/success/', views.esewa_success, name='esewa_success'),
    path('esewa/failure/', views.esewa_failure, name='esewa_failure'),
]
