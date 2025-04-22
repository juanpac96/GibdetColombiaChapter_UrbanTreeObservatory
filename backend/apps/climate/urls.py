from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StationViewSet, ClimateViewSet

app_name = "climate"

router = DefaultRouter()
router.register(r"stations", StationViewSet, basename="station")
router.register(r"data", ClimateViewSet, basename="climate")

urlpatterns = [
    path("", include(router.urls)),
]
