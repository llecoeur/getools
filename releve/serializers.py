"""
    Serialisers valables uniquement pour les relevés
"""

from rest_framework import serializers
from releve.models import SaisieSalarie

class SaisieSalarieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaisieSalarie
        fields = '__all__'