from enumfields import IntEnum, Enum


class InvoiceStatus(Enum):
    UNPAID = 'Unpaid'
    PAID = 'Paid'
    DEPOSIT = 'Deposit'
    OUTSTANDING = 'Outstanding'


class PayslipStatus(Enum):
    NOT_SENT = 'Not Sent'
    SENT = 'Sent'


class TaskStatus(Enum):
   CREATED = 'Created'
   PENDING = 'Pending'
   IN_PROGRESS = 'In Progress'
   COMPLETED = 'Completed'
   DECLINED = 'Declined'
