from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from listings.models import Listing


class SearchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_history',
        verbose_name=_('user'),
    )
    keyword = models.CharField(_('keyword'), max_length=255)
    searched_at = models.DateTimeField(_('searched at'), auto_now_add=True)

    class Meta:
        verbose_name = _('search query')
        verbose_name_plural = _('search history')
        ordering = ['-searched_at']
        indexes = [
            models.Index(fields=['keyword'], name='search_keyword_idx'),
        ]

    def __str__(self):
        return self.keyword

    def save(self, *args, **kwargs):
        self.keyword = self.keyword.strip().lower()
        super().save(*args, **kwargs)


class ViewHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='view_history',
        verbose_name=_('user'),
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name=_('listing'),
    )
    viewed_at = models.DateTimeField(_('viewed at'), auto_now_add=True)

    class Meta:
        verbose_name = _('listing view')
        verbose_name_plural = _('view history')
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['listing', 'viewed_at'], name='view_listing_date_idx'),
        ]

    def __str__(self):
        return f'View #{self.pk} of listing {self.listing_id}'