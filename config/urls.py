# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(
        template_name='auth/login.html',
        redirect_authenticated_user=True,
        next_page='dashboard'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),
    path('', include('web.urls')),
]