"""
    Serialisers valables uniquement pour les relevés
"""

from rest_framework import serializers
from releve.models import SaisieSalarie, ReleveSalarie, ReleveSalarieCommentaire

class SaisieSalarieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaisieSalarie
        fields = '__all__'

class ReleveSalarieSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleveSalarie
        fields = '__all__'

class ReleveSalarieCommentaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleveSalarieCommentaire
        fields = '__all__'