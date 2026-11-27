from rest_framework import serializers

from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id',
            'owner_name',
            'title',
            'description',
            'city',
            'district',
            'address',
            'price',
            'rooms',
            'property_type',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'is_active', 'created_at', 'updated_at']