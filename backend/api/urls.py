from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('login/', views.login, name='login'),
    path('sandwich-details/<int:user_id>/', views.get_sandwich_details, name='sandwich-details'),
] 