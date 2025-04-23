from django.contrib import admin
from django.utils.html import format_html

from .models import Measurement


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "biodiversity_record_display",
        "attribute_display",
        "measurement",
        "date",
    )
    list_filter = ("attribute", "unit", "method", "date")
    search_fields = ("biodiversity_record__id", "biodiversity_record__common_name")
    raw_id_fields = ("biodiversity_record",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "date"
    list_per_page = 25

    @admin.display(description="Bio Record")
    def biodiversity_record_display(self, obj):
        url = obj.biodiversity_record.get_admin_url()
        return format_html(
            '<a href="{}">Record #{}</a>', url, obj.biodiversity_record_id
        )

    @admin.display(description="Attribute")
    def attribute_display(self, obj):
        return obj.get_attribute_display()

    @admin.display(description="Measurement")
    def measurement(self, obj):
        return f"{obj.value} {obj.unit}"
