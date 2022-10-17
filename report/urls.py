from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include("move_journal.urls")),
] 

    
    
#print(settings.BASE_DIR, 'Привет', settings.MEDIA_URL, settings.MEDIA_ROOT)
#if settings.DEBUG:
#    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
