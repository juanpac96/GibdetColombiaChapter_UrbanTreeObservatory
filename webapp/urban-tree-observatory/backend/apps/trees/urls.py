from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"species", views.SpeciesViewSet)
router.register(r"trees", views.TreeViewSet)
router.register(r"maintenance", views.MaintenanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
