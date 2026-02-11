"""
Serializers for river APIs
"""
from rest_framework_gis import serializers
from core.models import River


class RiverSerializer(serializers.ModelSerializer):
    """Serializer for rivers."""

    class Meta:
        model = River
        fields = ('id', 'name', 'feature', 'state',
                  'region', 'miles', 'geometry')

        read_only_fields = ['id']


class RiverDetailSerializer(RiverSerializer):

    class Meta(RiverSerializer.Meta):
        fields = RiverSerializer.Meta.fields
        geo_field = 'geometry'
