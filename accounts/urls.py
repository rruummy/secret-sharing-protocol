from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Головна сторінка проєкту (/)
    path('', views.home_view, name='home'),
    
    # Сторінки автентифікації
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Особистий кабінет (панель користувача)
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
]