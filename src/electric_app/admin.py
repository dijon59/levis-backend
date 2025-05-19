from django.contrib import admin
from src.electric_app.models import Invoice, Quotation, Expense, Supplier, PaySlip, Task


@admin.register(Invoice)
class InvoiceModelAdmin(admin.ModelAdmin):
    list_display = ['customer_email', 'file', 'total_amount', 'created_at']
    list_filter = ('status', ('created_at', admin.DateFieldListFilter))


@admin.register(Quotation)
class QuotationModelAdmin(admin.ModelAdmin):
    list_display = ['customer_email', 'file', 'total_amount', 'created_at']


@admin.register(Expense)
class ExpenseModelAdmin(admin.ModelAdmin):
    list_display = ['description', 'created_at', 'amount']


@admin.register(PaySlip)
class PaySlipModelAdmin(admin.ModelAdmin):
    list_display = ['employee', 'hourly_rate', 'hours_worked', 'pay_amount', 'created_at']


@admin.register(Supplier)
class SupplierModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_number', 'email', 'address', 'created_at']


@admin.register(Task)
class TaskModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'status', 'is_accepted', 'created_at']
