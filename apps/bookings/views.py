from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Booking, BookingStatus
from .serializers import BookingSerializer


class BookingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Booking.objects.select_related('listing', 'tenant').filter(
            Q(tenant=user) | Q(listing__owner=user)
        )

        state = self.request.query_params.get('state')
        today = timezone.localdate()
        if state == 'active':
            queryset = queryset.filter(
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
                end_date__gte=today,
            )
        elif state == 'completed':
            queryset = queryset.filter(status=BookingStatus.CONFIRMED, end_date__lt=today)

        return queryset

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            return Response(
                {'detail': _('This booking cannot be cancelled.')},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if timezone.localdate() >= booking.start_date:
            return Response(
                {'detail': _('Bookings can be cancelled only before the check-in date.')},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = timezone.now()
        booking.save(update_fields=['status', 'cancelled_at', 'updated_at'])
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        booking = self.get_object()

        if booking.status != BookingStatus.PENDING:
            return Response(
                {'detail': _('Only pending bookings can be confirmed.')},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = BookingStatus.CONFIRMED
        booking.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        booking = self.get_object()  

        if booking.status != BookingStatus.PENDING:
            return Response(
                {'detail': _('Only pending bookings can be rejected.')},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = BookingStatus.REJECTED
        booking.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(booking).data)