from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _

from apps.core.models import SoftDeleteModel


MAX_ROOMS = 20


class PropertyType(models.TextChoices):
    APARTMENT = 'apartment', _('Apartment')
    HOUSE = 'house', _('House')
    STUDIO = 'studio', _('Studio')
    ROOM = 'room', _('Room')

class Listing(SoftDeleteModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='listings',
        verbose_name=_('owner'))
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'))

    city = models.CharField(_('city'), max_length=100)
    district = models.CharField(_('district'), max_length=100, blank=True)
    address = models.CharField(_('address'), max_length=255, blank=True)

    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))])

    rooms = models.PositiveSmallIntegerField(
        _('rooms'),
        validators=[MinValueValidator(1), MaxValueValidator(MAX_ROOMS)])
    property_type = models.CharField(_('property type'), max_length=20, choices=PropertyType.choices)

    is_active = models.BooleanField(_('active'), default=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('listing')
        verbose_name_plural = _('listings')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'city'], name='listing_active_city_idx'),
            models.Index(fields=['is_active', 'price'], name='listing_active_price_idx'),
            models.Index(fields=['is_active', 'property_type'], name='listing_active_type_idx'),
            models.Index(fields=['is_active', '-created_at'], name='listing_active_created_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gt=0),
                name='listing_price_positive',
            ),
            models.CheckConstraint(
                condition=Q(rooms__gte=1, rooms__lte=MAX_ROOMS),
                name='listing_rooms_range',
            ),
            models.CheckConstraint(
                condition=Q(property_type__in=PropertyType.values),
                name='listing_property_type_valid',
            ),
        ]

    def __str__(self):
        return f'{self.title} ({self.city})'

