from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='booking.tenant.first_name', read_only=True)
    listing = serializers.IntegerField(source='booking.listing_id', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'booking', 'listing', 'author_name', 'rating', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_booking(self, booking):
        if booking.tenant_id != self.context['request'].user.id:
            raise serializers.ValidationError(_('You can review only your own bookings.'))
        return booking

    def validate(self, attrs):
        if self.instance is not None:
            return attrs

        review = Review(**attrs)
        try:
            review.clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)

        return attrs