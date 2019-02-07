from rest_framework import serializers

from wattstrat.simulation.models import Simulation

class SimulationSerializer(serializers.ModelSerializer):
    creator = serializers.CharField(source='get_creator_name', read_only=True)
    creators = serializers.JSONField(read_only=True)
    territory_groups = serializers.JSONField()
    
    class Meta:
        model = Simulation
        fields = ('shortid', 'name', 'creator', 'creators', 'date', 'territory_groups')
