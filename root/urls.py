from django.urls import path, include
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from root.settings import MEDIA_ROOT, MEDIA_URL, STATIC_ROOT, STATIC_URL
from books.views import AdminStatsView

urlpatterns = [
    path('api/schema', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include("books.urls")),
    path('api/stats/', AdminStatsView.as_view()),
] + static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL, document_root=STATIC_ROOT)
