
from django.contrib import admin
from django.urls import path,include
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include("dashboard.urls")),
    path('accounting/', include("accounting.urls")),
    path('accounts/', include("accounting.urls")),
    path('', include("main.urls")),
    path('support', include("supportPlus.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)#
