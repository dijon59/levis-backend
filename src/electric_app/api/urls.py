from django.urls import path, re_path, include

from src.electric_app.api import views
from src.electric_app.routers import FlexiRouter
from src.accounts.api.urls import apis as accounts
from src.chat.api.urls import apis as chat


router = FlexiRouter()
router.register('quotation', views.QuotationViewset, basename='quotation')
router.register('invoice', views.InvoiceViewset, basename='invoice')
router.register('expense', views.ExpenseViewset, basename='expense')
router.register('payslip', views.PaySlipViewset, basename='payslip')
router.register('monthly-financial', views.MonthlyFinancialViewset, basename='monthly-financial')
router.register('supplier', views.SupplierViewset, basename='supplier')
router.register('export-expense', views.ExportExpensesView, basename='export-expense')
router.register('export-income', views.ExportIncomeView, basename='export-income')
router.register('task', views.TaskViewset, basename='task')
router.include(accounts, module='Accounts', prefix='accounts')
router.include(chat, module='Chat', prefix='chat')


urlpatterns = [
    re_path(r'^', include(router.urls)),
]
