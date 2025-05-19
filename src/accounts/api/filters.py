import django_filters
from django.utils.timezone import now
from django.db.models import Q
from datetime import timedelta
from src.accounts.models import User


class customerFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = User
        fields = {
            'name': ['exact'],  # Filter by status (Paid, Unpaid, etc.)
        }

    def filter_search(self, queryset, name, value):
        """ Search invoices by email and invoice_number"""
        return queryset.filter(
            Q(name__icontains=value) | Q(email__iexact=value)
        )
