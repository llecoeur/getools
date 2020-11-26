"""
    Serialisers valables uniquement pour les relevés
"""

from rest_framework import serializers
from releve.models import SaisieSalarie, ReleveSalarie

class SaisieSalarieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaisieSalarie
        fields = '__all__'

class ReleveSalarieSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleveSalarie
        fields = '__all__'