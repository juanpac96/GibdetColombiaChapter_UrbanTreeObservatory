from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CountryViewSet,
    DepartmentViewSet,
    MunicipalityViewSet,
    PlaceViewSet,
)

app_name = "places"

router = DefaultRouter()
router.register(r"countries", CountryViewSet, basename="country")
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"municipalities", MunicipalityViewSet, basename="municipality")
router.register(r"places", PlaceViewSet, basename="place")

urlpatterns = [
    path("", include(router.urls)),
]
