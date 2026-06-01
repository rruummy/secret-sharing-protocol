from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URL для авторизації та кабінету (додаток accounts)
    path('', include('accounts.urls')),
    
    # URL для роботи із секретами через шаблони (додаток secrets_app)
    path('secrets/', include('secrets_app.urls')),
    
    # URL для REST API (буде окремий додаток або модуль api, підключимо його сюди)
    # path('api/', include('api.urls')), 
]