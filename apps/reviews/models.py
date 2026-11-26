from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.bookings.models import Booking

MIN_RATING = 1
MAX_RATING = 5


class Review(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name=_('booking'),
    )
    text = models.TextField(_('text'), blank=True)
    rating = models.PositiveSmallIntegerField(
        _('rating'),
        validators=[MinValueValidator(MIN_RATING), MaxValueValidator(MAX_RATING)],
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('review')
        verbose_name_plural = _('reviews')
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=MIN_RATING, rating__lte=MAX_RATING),
                name='review_rating_range',
            ),
        ]

    def __str__(self):
        return f'Review #{self.pk} ({self.rating}/{MAX_RATING})'

    def clean(self):
        if self._state.adding and self.booking_id:
            from apps.bookings.models import BookingStatus

            if self.booking.status != BookingStatus.CONFIRMED:
                raise ValidationError(_('Only confirmed bookings can be reviewed.'))
            if self.booking.end_date > timezone.localdate():
                raise ValidationError(_('You can review only after your stay.'))
