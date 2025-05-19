from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import requests
from src.electric_app.models import Invoice, PaySlip, Quotation


class HtmlEmailSender:
    def __init__(self, subject, html_template, attachments=None, extra_context=None):
        # Email headers
        self.subject = subject
        self.sender = settings.DEFAULT_FROM_EMAIL
        self.attachments = attachments

        # Email body
        self.html_template = html_template
        self.context = {}
        self.context.update(extra_context)

    def render_html_body(self):
        return render_to_string(self.html_template, self.context)

    def send(self, to, cc=None, bcc=None):
        msg = EmailMessage(
            subject=self.subject,
            body=self.render_html_body(),
            from_email=self.sender,
            to=to,
            cc=cc,
            bcc=bcc,
            attachments=self.attachments,
        )
        msg.content_subtype = "html"
        msg.send()


def send_invoice_email(invoice: Invoice, pdf_url: str):
    # Fetch the PDF file from the S3 URL
    response = requests.get(pdf_url)
    if response.status_code == 200:
        filename = f'invoice_{invoice.id}.pdf'
        attachment = (filename, response.content, 'application/pdf')

        HtmlEmailSender(
            subject=f'Invoice-{invoice.invoice_number}',
            html_template='mails/invoice.html',
            extra_context={
                'customer_name': invoice.customer_name,
                'date': invoice.created_at,
            },
            attachments=[attachment],  # Django expects a list of (filename, content, mimetype)
        ).send(to=[invoice.customer_email])
    else:
        raise Exception(f"Failed to download PDF from {pdf_url}")


def send_invoice_follow_up(invoice: Invoice, pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        filename = f'invoice_{invoice.invoice_number}.pdf'
        attachment = (filename, response.content, 'application/pdf')
        HtmlEmailSender(
            subject='Invoice Follow up',
            html_template='mails/invoice-follow-up.html',
            extra_context={
                'customer_name': invoice.customer_name,
                'outstanding': invoice.outstanding_amount,
                'invoice_number': invoice.invoice_number,
                # 'quotation_number': Invoice,
            },
            attachments=[attachment]
        ).send(to=[invoice.customer_email])
    else:
        raise Exception(f"Failed to download PDF from {pdf_url}")


def send_quotation_follow_up(quotation: Quotation, pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        filename = f'quotation_{quotation.quotation_number}.pdf'
        attachment = (filename, response.content, 'application/pdf')
        HtmlEmailSender(
            subject='Quotation Follow up',
            html_template='mails/follow-up.html',
            extra_context={
                'customer_name': quotation.customer_name,
                'quotation_number': quotation.quotation_number,
            },
            attachments=[attachment],
        ).send(to=[quotation.customer_email])
    else:
        raise Exception(f"Failed to download PDF from {pdf_url}")


def send_quotation_email(quotation: Quotation, pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        filename = f'quotation_{quotation.quotation_number}.pdf'
        attachment = (filename, response.content, 'application/pdf')
        HtmlEmailSender(
            subject=f'Quotation-{quotation.quotation_number}',
            html_template='mails/quotation.html',
            extra_context={
                'customer_name': quotation.customer_name,
                # 'date': invoice.created_at,
            },
            attachments=[attachment],
        ).send(to=[quotation.customer_email])
    else:
        raise Exception(f"Failed to download PDF from {pdf_url}")


def send_payslip(payslip: PaySlip, pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        filename = f'payslip_{payslip.id}.pdf'
        attachment = (filename, response.content, 'application/pdf')

        HtmlEmailSender(
            subject='Weekly Payslip',
            html_template='mails/payslip.html',
            extra_context={
                'employee_name': payslip.employee.name,
                'date': payslip.created_at,
            },
            attachments=[attachment],
        ).send(to=[payslip.employee.email])
    else:
        raise Exception(f"Failed to download PDF from {pdf_url}")
