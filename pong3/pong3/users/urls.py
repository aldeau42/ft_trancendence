from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('success/', views.success_view, name='success'),
    path('login/', views.login_view, name="login"),
]