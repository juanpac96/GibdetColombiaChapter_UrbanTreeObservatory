from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Station, Climate


@admin.register(Station)
class StationAdmin(GISModelAdmin):
    list_display = ("code", "name")
    search_fields = ("name", "code")
    readonly_fields = ("id",)


@admin.register(Climate)
class ClimateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "station",
        "date",
        "sensor_display",
        "value",
        "measure_unit_display",
    )
    list_filter = ("station", "sensor", "measure_unit", "date")
    search_fields = ("station__name", "station__code")
    raw_id_fields = ("station", "municipality")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "date"
    list_per_page = 25

    @admin.display(description="Sensor")
    def sensor_display(self, obj):
        return obj.get_sensor_display()

    @admin.display(description="Unit")
    def measure_unit_display(self, obj):
        return obj.get_measure_unit_display()
