from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('login/', views.login, name='login'),
    path('sandwich-details/<int:user_id>/', views.get_sandwich_details, name='get_sandwich_details'),
    path('test-snowflake/', views.test_snowflake_connection, name='test_snowflake_connection'),
    path('check-customer-table/', views.check_customer_table, name='check_customer_table'),
    path('inspect-tables/', views.inspect_tables, name='inspect_tables'),
] 