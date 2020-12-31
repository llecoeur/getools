from rest_framework import serializers
from activite import models


class SalarieSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Salarie
        fields = '__all__'