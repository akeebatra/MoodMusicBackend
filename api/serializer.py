from rest_framework import serializers
from api.models import Tracks

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracks
        fields = ['id','name', 'uri','href','duration_ms']