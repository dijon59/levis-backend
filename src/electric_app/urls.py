from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    # path('sentry-debug/', trigger_error),
    path('admin/', admin.site.urls),
    path('api/', include('src.electric_app.api.urls'))
]

# this will serve image files during development
# for production we will be using s3 bucket to serve files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
