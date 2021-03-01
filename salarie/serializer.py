from rest_framework import serializers
from salarie import models

class CalendrierSalarieSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CalendrierSalarie
        fields = '__all__'


class CalendrierSalariePeriodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CalendrierSalariePeriode
        fields = '__all__'


class CalendrierSalarieMiseADispositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CalendrierSalarieMiseADisposition
        fields = '__all__'


        