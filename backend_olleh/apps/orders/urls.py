from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.orders.views import LayawayViewSet

app_name = "orders"

router = DefaultRouter()
router.register(r"layaways", LayawayViewSet, basename="layaway")

urlpatterns = [
    path("", include(router.urls)),
]
