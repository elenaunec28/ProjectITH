from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

from .listing import Listing


class Booking(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает подтверждения'
        CONFIRMED = 'confirmed', 'Подтверждено'
        REJECTED = 'rejected', 'Отклонено'
        CANCELLED = 'cancelled', 'Отменено'

    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings',)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING,)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.tenant} → {self.listing} ({self.start_date} – {self.end_date})'