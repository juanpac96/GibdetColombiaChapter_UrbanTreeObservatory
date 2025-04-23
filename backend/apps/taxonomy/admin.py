# apps/taxonomy/admin.py
from django.contrib import admin
from .models import Family, Genus, Species, FunctionalGroup, Trait


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")
    list_per_page = 100


@admin.register(Genus)
class GenusAdmin(admin.ModelAdmin):
    list_display = ("name", "family")
    list_filter = ("family",)
    search_fields = ("name", "family__name")
    readonly_fields = ("id", "created_at", "updated_at")
    list_per_page = 100


class SpeciesInline(admin.TabularInline):
    model = Species
    extra = 0
    fields = ("name", "genus")


@admin.register(FunctionalGroup)
class FunctionalGroupAdmin(admin.ModelAdmin):
    list_display = ("group_str", "trait_count", "created_at")
    search_fields = ("group_id",)
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [SpeciesInline]

    @admin.display(description="Group")
    def group_str(self, obj):
        return str(obj)

    @admin.display(description="Number of Traits")
    def trait_count(self, obj):
        return obj.traits.count()


@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "get_type_display", "created_at")
    search_fields = ("type",)


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = (
        "scientific_name",
        "life_form_display",
        "origin_display",
        "iucn_status_display",
    )
    list_filter = ("life_form", "origin", "iucn_status", "genus__family")
    search_fields = ("name", "genus__name", "accepted_scientific_name")
    raw_id_fields = ("genus", "functional_group")
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "scientific_name",
        "gbif_url",
        "tropical_plants_url",
    )
    fieldsets = (
        (
            "Taxonomy",
            {
                "fields": (
                    "genus",
                    "name",
                    "accepted_scientific_name",
                    "scientific_name",
                )
            },
        ),
        (
            "Classification",
            {"fields": ("origin", "iucn_status", "life_form", "functional_group")},
        ),
        ("Physical Characteristics", {"fields": ("canopy_shape", "flower_color")}),
        (
            "External References",
            {"fields": ("gbif_id", "gbif_url", "tropical_plants_url")},
        ),
        ("Identification", {"fields": ("identified_by", "date")}),
        ("Metadata", {"fields": ("id", "created_at", "updated_at")}),
    )

    @admin.display(description="Life Form")
    def life_form_display(self, obj):
        return obj.get_life_form_display()

    @admin.display(description="Origin")
    def origin_display(self, obj):
        return obj.get_origin_display()

    @admin.display(description="IUCN Status")
    def iucn_status_display(self, obj):
        return obj.get_iucn_status_display()
