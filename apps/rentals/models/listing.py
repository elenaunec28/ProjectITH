from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Listing(models.Model):

    class PropertyType(models.TextChoices):
        APARTMENT = 'apartment', 'Квартира'
        HOUSE = 'house', 'Дом'
        STUDIO = 'studio', 'Студия'
        ROOM = 'room', 'Комната'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    rooms = models.PositiveSmallIntegerField( validators=[MinValueValidator(1)])
    property_type = models.CharField(max_length=20, choices=PropertyType.choices)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.city})'

