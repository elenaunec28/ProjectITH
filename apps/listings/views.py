from django.db.models import ProtectedError, Q
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.analytics.models import ViewHistory

from .models import Listing
from .serializers import ListingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Listing.objects.select_related('owner')
        user = self.request.user
        if user.is_authenticated:
            return queryset.filter(Q(is_active=True) | Q(owner=user))
        return queryset.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        listing = self.get_object()
        ViewHistory.objects.create(
            listing=listing,
            user=request.user if request.user.is_authenticated else None,
        )
        return Response(self.get_serializer(listing).data)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': _('This listing has bookings and cannot be deleted. Deactivate it instead.')},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        listing = self.get_object()
        listing.is_active = not listing.is_active
        listing.save(update_fields=['is_active', 'updated_at'])
        return Response(self.get_serializer(listing).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        listings = Listing.objects.filter(owner=request.user)
        page = self.paginate_queryset(listings)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)