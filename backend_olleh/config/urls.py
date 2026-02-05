"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, re_path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.common.views import PoliciesViewSet
from users.views import MemberProfileViewSet, MemberMeasurementsViewSet

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"^auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
    # YOUR PATTERNS
    path("api/", include("apps.memberships.urls")),
    path("api/savings/", include("apps.savings.urls")),
    path("api/", include("apps.orders.urls")),
    path(
        "api/policies/",
        PoliciesViewSet.as_view(actions={"get": "list"}),
        name="policies-list",
    ),
    path(
        "api/me/profile/",
        MemberProfileViewSet.as_view(actions={"get": "list", "patch": "partial_update"}),
        name="me-profile",
    ),
    path(
        "api/me/measurements/",
        MemberMeasurementsViewSet.as_view(actions={"get": "list", "post": "create"}),
        name="me-measurements",
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
