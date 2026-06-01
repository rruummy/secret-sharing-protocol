from django.urls import path
from . import views

app_name = 'secrets_app'

urlpatterns = [
    # Список секретів (/secrets/)
    path('', views.secret_list_view, name='list'),
    
    # Створення секрету (/secrets/create/)
    path('create/', views.secret_create_view, name='create'),
    
    # Перегляд секрету (/secrets/<id>/)
    path('<int:pk>/', views.secret_detail_view, name='detail'),
    
    # Перегляд часток (/secrets/<id>/shares/)
    path('<int:pk>/shares/', views.share_list_view, name='shares'),
    
    # Відновлення секрету (/recover/) — винесемо в корінь цього додатка, щоб URL був /recover/
    path('recover/', views.secret_recover_view, name='recover'),
]