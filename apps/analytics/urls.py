from django.urls import path

from .views import PopularListingsView, PopularSearchesView

urlpatterns = [
    path('analytics/popular-searches/', PopularSearchesView.as_view(), name='popular-searches'),
    path('analytics/popular-listings/', PopularListingsView.as_view(), name='popular-listings'),
]