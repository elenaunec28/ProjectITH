from datetime import timedelta
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _

from apps.listings.models import Listing


MAX_BOOKING_HORIZON = timedelta(days=360)


class BookingStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    CONFIRMED = 'confirmed', _('Confirmed')
    REJECTED = 'rejected', _('Rejected')
    CANCELLED = 'cancelled', _('Cancelled')


class Booking(models.Model):
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name=_('tenant'))

    listing = models.ForeignKey(
        Listing,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name=_('listing'))

    start_date = models.DateField(_('check-in date'))
    end_date = models.DateField(_('check-out date'))

    total_price = models.DecimalField(
        _('total price'),
        max_digits=10,
        decimal_places=2,
        editable=False)

    status = models.CharField(
        _('status'),
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('booking')
        verbose_name_plural = _('bookings')
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gt=F('start_date')),
                name='booking_end_after_start',
            ),
            models.CheckConstraint(
                condition=Q(status__in=BookingStatus.values),
                name='booking_status_valid',
            ),
            models.CheckConstraint(
                condition=Q(total_price__gt=0),
                name='booking_total_price_positive',
            ),
            models.CheckConstraint(
                condition=(
                    Q(status=BookingStatus.CANCELLED, cancelled_at__isnull=False)
                    | (~Q(status=BookingStatus.CANCELLED) & Q(cancelled_at__isnull=True))
                ),
                name='booking_cancelled_at_matches_status',
            ),
        ]

    def __str__(self):
        return f'Booking #{self.pk} ({self.start_date} – {self.end_date})'

    def clean(self):
        super().clean()

        if not self._state.adding:
            return
        if not (self.listing_id and self.start_date and self.end_date):
            return

        errors = []

        if self._state.adding:
            if self.start_date and self.start_date < timezone.localdate():
                errors.append(_('Check-in date cannot be in the past.'))

            if self.start_date and self.start_date > timezone.localdate() + MAX_BOOKING_HORIZON:
                errors.append(_('Bookings can be made no more than 360 days in advance.'))

            if self.listing_id:
                if not self.listing.is_active:
                    errors.append(_('This listing is not available.'))
                if self.listing.owner_id == self.tenant_id:
                    errors.append(_('You cannot book your own listing.'))

            if self.listing_id and self.start_date and self.end_date:
                overlapping = Booking.objects.filter(
                    listing_id=self.listing_id,
                    status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
                    start_date__lt=self.end_date,
                    end_date__gt=self.start_date,
                )
                if overlapping.exists():
                    errors.append(_('These dates are already booked.'))

        if errors:
            raise ValidationError(errors)

    def calculate_total_price(self):
        nights = (self.end_date - self.start_date).days
        return self.listing.price * nights

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)