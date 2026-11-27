from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _


username_validator = RegexValidator(
    regex=r'^[\w.-]+\Z',
    message=_('Username may contain only letters, digits and the characters . _ -'),
)
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
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField(_('email'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

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
            models.UniqueConstraint(
                Lower('username'),
                name='user_username_unique_case_insensitive',
                violation_error_message=_('A user with this username already exists.'),
            ),
            models.CheckConstraint(
                condition=~Q(username__contains='@'),
                name='user_username_not_email',
                violation_error_message=_('Username cannot contain "@".'),
            ),
            models.CheckConstraint(
                condition=~Q(first_name='') & ~Q(last_name=''),
                name='user_names_not_empty',
                violation_error_message=_('First and last name are required.'),
            ),
        ]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        self.username = self.username.strip()
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        super().save(*args, **kwargs)