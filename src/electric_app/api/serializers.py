from rest_framework import serializers
from src.electric_app.utils import PDFGeneration
from src.electric_app.enums import InvoiceStatus
from src.accounts.api.serializers import UserSerializer
from src.electric_app.models import Customer, Expense, Invoice, PaySlip, Quotation, Supplier, Task
from src.accounts.models import User


class CustomerSerializer(serializers.ModelSerializer):
    """
     Serializer dedicated for the creation of customer objects
    """
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = (
            'id',
            'user',
        )


class InvoiceSerializer(serializers.ModelSerializer):
    info = serializers.JSONField(required=True)
    created_at = serializers.DateField(read_only=True)
    file = serializers.FileField(read_only=True)
    invoice_number = serializers.CharField(required=False)
    specific_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Invoice
        fields = (
            'id',
            'customer_email',
            'customer_name',
            'contact_number',
            'customer_address',
            'invoice_number',
            'amount_paid',
            'outstanding_amount',
            'info',
            'is_sent',
            'is_follow_up_sent',
            'created_at',
            'file',
            'status',
            'total_amount',
            'specific_date',
        )

    def to_representation(self, instance: Invoice):
        representation = super().to_representation(instance)
        representation['created_at'] = instance.created_at.strftime('%Y-%m-%d')
        representation['specific_date'] = instance.specific_date.strftime('%Y-%m-%d') if instance.specific_date else None
        representation['status'] = instance.status.value
        return representation

    def get_filename(self, invoice):
        filename = f"invoice_{invoice.id}.pdf"
        return filename

    def calculate_deposit(self, amount=0.00):
        """
        Deposit should be 70% of total amount
        """
        return (amount * 70)/100

    def calculate_outstanding_amount (self, amount_paid=0.00, total_amount=0.00):
        # if amount_paid < 1:
        #     return 0.00
        return total_amount - amount_paid

    def get_template_path(self):
        return "pdf/invoice.html"

    def update(self, instance, validated_data):

        if validated_data['amount_paid'] >= instance.total_amount:
             validated_data['outstanding_amount'] = 0.00
             validated_data['status'] = InvoiceStatus.PAID

        elif validated_data['amount_paid'] <= 0:
            validated_data['outstanding_amount'] = 0.00
            validated_data['status'] = InvoiceStatus.UNPAID

        else :
            validated_data['outstanding_amount'] = self.calculate_outstanding_amount(validated_data['amount_paid'], instance.total_amount)
            validated_data['status'] = InvoiceStatus.OUTSTANDING

        updated_instance: Invoice = super().update(instance, validated_data)
        PDFGeneration(updated_instance, self.get_template_path(), self.get_filename(updated_instance)).generate_pdf()
        return updated_instance

    def create(self, validated_data):
        try:
            customer = User.objects.get(email=validated_data.get('customer_email'))
            if customer:
                return super().create(validated_data)
        except User.DoesNotExist:
            customer = User.objects.create(
                email=validated_data.get('customer_email'),
                contact_number=validated_data.get('contact_number'),
                address=validated_data.get('customer_address'),
                name=validated_data.get('customer_name'),
                is_customer=True)
            return super().create(validated_data)


class QuotationSerializer(InvoiceSerializer):
    quotation_number = serializers.CharField(required=False)

    class Meta:
        model = Quotation
        fields = (
            'id', 
            'customer_email',
            'customer_name',
            'contact_number',
            'customer_address',
            'quotation_number',
            'amount_paid',
            'outstanding_amount',
            'info',
            'created_at',
            'file',
            'total_amount',
            'is_sent',
            'is_follow_up_sent',
            'specific_date',
        )

    def get_template_path(self):
        return "pdf/quotation.html"

    def get_filename(self, quotation):
        filename = f"quotation_{quotation.id}.pdf"
        return filename


class ExpenseSerializer(serializers.ModelSerializer):
    specific_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Expense
        fields = ('__all__')

    def to_representation(self, instance: Invoice):
        representation = super().to_representation(instance)
        representation['created_at'] = instance.created_at.strftime('%Y-%m-%d')
        representation['specific_date'] = instance.specific_date.strftime('%Y-%m-%d') if instance.specific_date else None
        return representation


class PaySlipSeriliazer(serializers.ModelSerializer):
    pay_amount = serializers.DecimalField(required=False, decimal_places=2, max_digits=100)
    overtime_pay = serializers.DecimalField(required=False, decimal_places=2, max_digits=100)
    commission = serializers.DecimalField(required=False, decimal_places=2, max_digits=100)
    bonus = serializers.DecimalField(required=False, decimal_places=2, max_digits=100)
    deduction = serializers.DecimalField(required=False, decimal_places=2, max_digits=100)
    specific_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = PaySlip
        fields = ('__all__')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['employee'] = UserSerializer(instance.employee).data
        representation['created_at'] = instance.created_at.strftime('%Y-%m-%d')
        representation['specific_date'] = instance.specific_date.strftime('%Y-%m-%d') if instance.specific_date else None
        representation['status'] = instance.status.value
        return representation

    def update(self, instance, validated_data):
        updated_instance = super().update(instance, validated_data)
        PDFGeneration(updated_instance, 'pdf/payslip.html' , f"payslip_{updated_instance.id}.pdf").generate_pdf()
        return updated_instance

    def create(self, validated_data):
        instance = super().create(validated_data)
        PDFGeneration(instance, "pdf/payslip.html", f"payslip_{instance.id}.pdf").generate_pdf()
        return instance


class SuppliersSeriliazer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ('__all__')


class TaskSerializer(serializers.ModelSerializer):
    before_work_picture = serializers.ImageField(required=False)
    after_work_picture = serializers.ImageField(required=False)
    customer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        client = self.context.get('request').headers.get('X-Client', '').lower()
        
        if client == 'flutter':
            self.fields['description'].read_only = True
        else:
            self.fields['description'].required = False

    class Meta:
        model = Task
        fields = ('__all__')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_at'] = instance.created_at.strftime('%Y-%m-%d')
        representation['status'] = instance.status.value
        representation['assignees'] = UserSerializer(instance.assignees, many=True).data
        representation['customer'] = UserSerializer(instance.customer).data
        return representation
