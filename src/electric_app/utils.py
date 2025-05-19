import io
from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings


class PDFGeneration:
    def __init__(self, object, template_path, filename):
        self.object = object
        self.template_path = template_path
        self.filename = filename

    def generate_pdf(self):
        try:
            if hasattr(self.object, 'invoice_number') or hasattr(self.object, 'quotation_number'):
                context = {
                    'is_quotation': hasattr(self.object, 'quotation_number'),
                    'id': self.object.invoice_number if hasattr(self.object, 'invoice_number') else self.object.quotation_number,
                    'date': self.object.specific_date.strftime('%Y-%m-%d') if self.object.specific_date else self.object.created_at.strftime('%Y-%m-%d'),
                    'email': self.object.customer_email,
                    'name': self.object.customer_name,
                    'contact_number': self.object.contact_number,
                    'address': self.object.customer_address,
                    'info': self.object.info,
                    'deposit': (self.object.total_amount * 70)/100,
                    'remaining': (self.object.total_amount * 30)/100,
                    'total': self.object.total_amount,
                    'outstanding': self.object.outstanding_amount,
                    'amount_paid': self.object.amount_paid,
                }

            else:

                context = {
                    'name': self.object.employee.name,
                    'employee_number': f'0{self.object.id}',
                    'role': self.object.employee.role.value,
                    'hours_worked': self.object.hours_worked,
                    'hourly_rate': self.object.hourly_rate,
                    'amount': self.object.pay_amount,
                    'overtime_pay': self.object.overtime_pay,
                    'commission': self.object.commission,
                    'bonus': self.object.bonus,
                    'gross': self.object.gross,
                    'net': self.object.net_pay,
                    'deduction': self.object.deduction,
                    'signed_at': self.object.specific_date if self.object.specific_date else self.object.created_at,
                    'BASE_URL': settings.BASE_URL, 
                }

            html_data = render_to_string(self.template_path,
            context,
            )

            # Generate PDF in memory
            pdf_file = HTML(string=html_data).write_pdf()
            buff = io.BytesIO()
            buff.write(pdf_file)
            buff.seek(0)

            # Create the PDF file
            # filename = f"invoice_{invoice.id}.pdf"
            # self.set_filename(invoice)
            pdf_attach = [(self.filename, buff.getvalue(), 'application/pdf')]

            # Save PDF directly using Django's file storage
            self.object.file.save(
                name=self.filename,
                content=ContentFile(buff.getvalue()),
                save=True
            )

            self.object.refresh_from_db()
            return pdf_attach

        finally:
            # Clean up resources
            if 'buff' in locals():
                buff.close()
