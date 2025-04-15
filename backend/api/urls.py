from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('login/', views.login, name='login'),
    path('sandwich-details/<int:user_id>/', views.get_sandwich_details, name='get_sandwich_details'),
    path('test-snowflake/', views.test_snowflake_connection, name='test_snowflake_connection'),
    path('check-customer-table/', views.check_customer_table, name='check_customer_table'),
    path('inspect-tables/', views.inspect_tables, name='inspect_tables'),
    path('customer/<str:customer_key>/favorite-sandwich/', views.get_customer_favorite_sandwich, name='customer-favorite-sandwich'),
    path('customer/<str:customer_key>/sandwich-report/', views.get_customer_sandwich_report, name='customer-sandwich-report'),
] 