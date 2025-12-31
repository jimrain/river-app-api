"""
Serializers for river APIs
"""
from rest_framework import serializers

from core.models import River


class RiverSerializer(serializers.ModelSerializer):
    """Serializer for rivers."""

    class Meta:
        model = River
        fields = ['id', 'name', 'feature', 'state',
                  'region', 'miles', 'geometry_type', ]
        read_only_fields = ['id']


class RiverDetailSerializer(RiverSerializer):

    coordinates = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField(),
                                    min_length=2, max_length=2),
        allow_empty=False
    )

    class Meta(RiverSerializer.Meta):
        fields = RiverSerializer.Meta.fields + ['coordinates', ]
