"""
Root URL configuration for GymBro.

All application routes are versioned under /api/<version>/ using DRF's
URLPathVersioning (configured in settings.REST_FRAMEWORK).

Currently supported version: v1

Route map:
  /api/v1/users/   → apps.users.urls   (auth + profile)
  /api/v1/gym/     → apps.workouts.urls
  /api/v1/iq/      → apps.exercises.urls
  /api/v1/blog/    → apps.blog.urls
  /api/v1/bros/    → apps.bros.urls

Schema / docs (version-agnostic):
  /api/schema/     → OpenAPI schema (JSON)
  /api/docs/       → Swagger UI
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Versioned API routes — all app URL confs are nested under /api/<version>/
versioned_patterns = [
    path("users/", include("apps.users.urls")),
    path("gym/", include("apps.workouts.urls")),
    path("iq/", include("apps.exercises.urls")),
    path("blog/", include("apps.blog.urls")),
    path("bros/", include("apps.bros.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),

    # Versioned API — DRF URLPathVersioning reads the <version> capture group
    path("api/<version>/", include(versioned_patterns)),

    # OpenAPI schema & Swagger UI (not versioned — always reflects current API)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
