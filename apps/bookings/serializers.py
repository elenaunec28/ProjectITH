from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    tenant_name = serializers.CharField(source='tenant.username', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'listing',
            'listing_title',
            'tenant_name',
            'start_date',
            'end_date',
            'total_price',
            'status',
            'cancelled_at',
            'created_at',
        ]
        read_only_fields = ['id', 'total_price', 'status', 'cancelled_at', 'created_at']

    def validate(self, attrs):
        if self.instance is not None:
            return attrs

        if attrs['end_date'] <= attrs['start_date']:
            raise serializers.ValidationError(
                {'end_date': _('Check-out date must be after check-in date.')}
            )

        booking = Booking(tenant=self.context['request'].user, **attrs)
        try:
            booking.clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)

        return attrs