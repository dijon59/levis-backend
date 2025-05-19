from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import EnumField
from src.electric_app.utils import PDFGeneration
from src.accounts.models import User
from .enums import InvoiceStatus, PayslipStatus, TaskStatus


_OPTIONAL = {'blank': True, 'null': True}


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.email


class InvoiceAbstract(models.Model):
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=100, **_OPTIONAL)
    contact_number = models.CharField(max_length=15, **_OPTIONAL)
    customer_address = models.CharField(max_length=500, **_OPTIONAL)
    info = models.JSONField(default=[])
    status = EnumField(InvoiceStatus, default=InvoiceStatus.UNPAID, max_length=250)
    created_at = models.DateField(auto_now_add=True)
    file = models.FileField(upload_to='invoices/', default='')
    total_amount = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    outstanding_amount = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    is_sent = models.BooleanField(default=False)
    is_follow_up_sent = models.BooleanField(default=False)
    specific_date = models.DateField(**_OPTIONAL)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.id} for {self.customer_email}"


class Invoice(InvoiceAbstract):
    """
        Invoice to be sent to customer
    """
    invoice_number = models.CharField(max_length=250, unique=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.total_amount = 0.00

        for i in self.info:
            self.total_amount += int(i['unit']) * i['amount']

        super_result = super().save(force_insert, force_update, using, update_fields)

        # Generate quotation number after saving
        if not self.invoice_number:
            # Adjust formatting based on ID length
            if self.id < 10:
                self.invoice_number = f"INV-000{self.id}"
            elif self.id < 1000:
                self.invoice_number = f"INV-0{self.id}"
            else:
                self.invoice_number = f"INV-{self.id}"

            # Update the model with the quotation number
            super().save(update_fields=['invoice_number'])
            PDFGeneration(self, "pdf/invoice.html", f"invoice_{self.invoice_number}.pdf").generate_pdf()
        return super_result


class Quotation(InvoiceAbstract):
    """
        Quotation to be sent to customer
    """
    quotation_number = models.CharField(max_length=250, unique=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.total_amount = 0.00

        for i in self.info:
            self.total_amount += int(i['unit']) * i['amount']

        super_result = super().save(force_insert, force_update, using, update_fields)

        # Generate quotation number after saving
        if not self.quotation_number:
            # Adjust formatting based on ID length
            if self.id < 10:
                self.quotation_number = f"QUO-000{self.id}"
            elif self.id < 1000:
                self.quotation_number = f"QUO-0{self.id}"
            else:
                self.quotation_number = f"QUO-{self.id}"

            # Update the model with the quotation number
            super().save(update_fields=['quotation_number'])
            PDFGeneration(self, "pdf/quotation.html", f"invoice_{self.quotation_number}.pdf").generate_pdf()
        return super_result


class Expense(models.Model):
    invoice_number = models.CharField(max_length=500, default='', **_OPTIONAL)
    supplier_name = models.CharField(max_length=250, default='')
    description = models.CharField(max_length=500, default='')
    created_at = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    specific_date = models.DateField(**_OPTIONAL)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ['-created_at']


class PaySlip(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    hourly_rate =  models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    hours_worked = models.PositiveIntegerField(default=0)
    pay_amount =  models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    overtime_pay = models.DecimalField(max_digits=100, decimal_places=2, default=0.00, blank=True)
    commission = models.DecimalField(max_digits=100, decimal_places=2, default=0.00, blank=True)
    bonus = models.DecimalField(max_digits=100, decimal_places=2, default=0.00, blank=True)
    status = EnumField(PayslipStatus, default=PayslipStatus.NOT_SENT)
    created_at = models.DateField(auto_now_add=True)
    file = models.FileField(upload_to='payslip/', default='', **_OPTIONAL)
    deduction = models.DecimalField(max_digits=100, decimal_places=2, default=0.00, blank=True)
    gross = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    net_pay = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    specific_date = models.DateField(**_OPTIONAL)

    def __str__(self):
        return self.employee.email

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.pay_amount = self.hourly_rate * Decimal(self.hours_worked)
        self.gross = self.pay_amount + self.overtime_pay + self.commission + self.bonus - self.deduction
        self.net_pay = self.gross # just for now.

        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ['-created_at']


class Supplier(models.Model):
    name = models.CharField(max_length=500)
    contact_number = models.CharField(max_length=15, **_OPTIONAL)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=500, **_OPTIONAL)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Task(models.Model):
    assignees = models.ManyToManyField(User, related_name='tasks')
    customer = models.ForeignKey(User, on_delete=models.CASCADE,  **_OPTIONAL)
    name = models.CharField(max_length=250, **_OPTIONAL)
    description = models.TextField(**_OPTIONAL)
    before_work_picture = models.ImageField(upload_to='tasks',  **_OPTIONAL)
    after_work_picture = models.ImageField(upload_to='tasks',  **_OPTIONAL)
    work_description = models.TextField(**_OPTIONAL)
    created_at = models.DateTimeField(auto_now_add=True)
    status = EnumField(TaskStatus, default=TaskStatus.CREATED, max_length=20)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} - {self.id}'

    class Meta:
        ordering = ['-created_at']

    @property
    def assignee_ids(self):
        return list(self.assignee.all().values_list('id', flat=True))
