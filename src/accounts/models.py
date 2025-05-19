from django.db import models
from django.db.models import Q, UniqueConstraint
from django.contrib.auth.models import AbstractUser
from src.accounts.user_manager import CustomUserManager
from django.utils.translation import gettext_lazy as _
from enumfields import EnumField
from .enums import Role


_OPTIONAL = {'blank': True, 'null': True}


class AbstractEmailUser(AbstractUser):
    username = None
    email = models.EmailField(_('Email Address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        abstract = True
        ordering = ['email', '-date_joined']

    def __str__(self):
        return self.email


class User(AbstractEmailUser):
    contact_number = models.CharField(max_length=30, **_OPTIONAL)
    address = models.CharField(max_length=500, default='', **_OPTIONAL)
    is_customer = models.BooleanField(default=False)
    name = models.CharField(max_length=250, default='')
    is_employee = models.BooleanField(default=False)
    role = EnumField(Role, default=Role.ELECTRICIAN, max_length=20)

    class Meta:
        constraints = [
            # Only enforce uniqueness for non-customers
            UniqueConstraint(
                fields=['contact_number'],
                condition=Q(is_customer=False),
                name='unique_contact_number_for_non_customers'
            ),
        ]


class FCMDeviceToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_token = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
