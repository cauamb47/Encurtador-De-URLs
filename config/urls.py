from django.contrib import admin
from django.urls import include, path

from links.views import redirect_to_original

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("links.urls")),
    path("<str:code>/", redirect_to_original, name="redirect"),
]