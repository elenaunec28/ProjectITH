from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email is required'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='unique_email_case_insensitive',
                violation_error_message=_('A user with this email already exists.'),
            ),
        ]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)