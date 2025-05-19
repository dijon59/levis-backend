import django_filters
from django.utils.timezone import now
from django.db.models import Q
from datetime import timedelta
from src.electric_app.models import Invoice, Quotation, Task


class DateFilter(django_filters.FilterSet):
    date_filter = django_filters.CharFilter(method='filter_by_date')

    def filter_by_date(self, queryset, name, value):
        """ Filter invoices by specific day, week, or month. """
        today = now().date()

        if value == 'today':
            return queryset.filter(
                Q(specific_date__isnull=True, created_at=today) |
                Q(specific_date__isnull=False, specific_date=today))
        elif value == 'week':
            start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
            return queryset.filter(
                Q(specific_date__isnull=False, specific_date__gte=start_of_week) | 
                Q(specific_date__isnull=True, created_at__gte=start_of_week))

        elif value == 'month':
            return queryset.filter(
                Q(specific_date__isnull=True, created_at__month=today.month, created_at__year=today.year) | 
                Q(specific_date__isnull=False, specific_date__month=today.month, specific_date__year=today.year))
        
        elif value == 'last_month':
            if today.month == 1:
                last_month = 12
                year = today.year - 1
            else:
                last_month = today.month - 1
                year = today.year

            return queryset.filter(
                Q(specific_date__isnull=True, created_at__month=last_month, created_at__year=year) | 
                Q(specific_date__isnull=False, specific_date__month=last_month, specific_date__year=year)
            )
        return queryset  # If no match, return unfiltered queryset


# class FilterSearchMixin:
#     def filter_search(self, queryset, name, value):
#         """ Search invoices by email and invoice_number"""
#         return queryset.filter(
#             Q(customer_name__icontains=value) | Q(customer_email__icontains=value) | Q(invoice_number__iexact=value)
#         )


class InvoiceFilter(DateFilter):
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Invoice
        fields = {
            'status': ['exact'],  # Filter by status (Paid, Unpaid, etc.)
        }

    def filter_search(self, queryset, name, value):
        """ Search invoices by email and invoice_number"""
        return queryset.filter(
            Q(customer_name__icontains=value) | Q(customer_email__icontains=value) | Q(invoice_number__iexact=value)
        )


class QuotationFilter(InvoiceFilter):
    class Meta:
        model = Quotation
        fields = {
            'status': ['exact'],
        }

    def filter_search(self, queryset, name, value):
        """ Search quotation by email and quotation_number"""
        return queryset.filter(
            Q(customer_name__icontains=value) | Q(customer_email__icontains=value) | Q(quotation_number__iexact=value)
        )


class TaskFilter(django_filters.FilterSet):
    date_filter = django_filters.CharFilter(method='filter_by_date')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Task
        fields = {
            'status': ['exact'],  # Filter by status 
        }

    def filter_search(self, queryset, name, value):
        """ Search tasks by name, customer name, customer email"""
        return queryset.filter(
            Q(name__icontains=value) | Q(customer__name__icontains=value) | Q(customer__email__iexact=value)
        )

    def filter_by_date(self, queryset, name, value):
        """ Filter invoices by specific day, week, or month. """
        today = now().date()

        if value == 'today':
            return queryset.filter(created_at=today)
        elif value == 'week':
            start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
            return queryset.filter(created_at__gte=start_of_week)

        elif value == 'month':
            return queryset.filter(created_at__month=today.month, created_at__year=today.year)

        return queryset
