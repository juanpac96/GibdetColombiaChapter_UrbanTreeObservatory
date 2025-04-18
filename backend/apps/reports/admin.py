from django.contrib import admin
from .models import Measurement, Observation


admin.site.register(Measurement)
admin.site.register(Observation)
