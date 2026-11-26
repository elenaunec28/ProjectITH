from django.db.models import Count
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.listings.models import Listing
from apps.listings.serializers import ListingSerializer

from .models import SearchHistory
from .serializers import PopularSearchSerializer


class PopularSearchesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        popular = (
            SearchHistory.objects
            .values('keyword')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        serializer = PopularSearchSerializer(popular, many=True)
        return Response(serializer.data)


class PopularListingsView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Listing.objects
            .filter(is_active=True)
            .select_related('owner')
            .annotate(views_count=Count('views'))
            .order_by('-views_count', '-created_at')
        )
