
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include("dashboard.urls")),
    path('accounting/', include("accounting.urls")),
    path('', include("main.urls")),
]
