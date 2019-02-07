from django.contrib import admin
from wattstrat.simulation.models import Simulation

@admin.register(Simulation)
class SimulationAdmin(admin.ModelAdmin):
    readonly_fields = ('shortid', 'date')
    exclude = ()
