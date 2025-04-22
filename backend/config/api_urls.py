from django.urls import path, include

urlpatterns = [
    path("taxonomy/", include("apps.taxonomy.urls")),
    path("places/", include("apps.places.urls")),
    # path('biodiversity/', include('apps.biodiversity.urls')),
    # path('reports/', include('apps.reports.urls')),
]
