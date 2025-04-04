from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/user/", include("user.urls", namespace="user")),
    path("api/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)  # NOQA W503
