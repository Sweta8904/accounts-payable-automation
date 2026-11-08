from django.urls import path

from .views import (
    InvoiceListCreateView,
    InvoiceApprovalView,
    InvoiceDashboardView,
)

urlpatterns = [
    path("", InvoiceListCreateView.as_view(), name="invoice-list-create"),

    path(
        "dashboard/",
        InvoiceDashboardView.as_view(),
        name="invoice-dashboard"
    ),

    path(
        "<int:pk>/approval/",
        InvoiceApprovalView.as_view(),
        name="invoice-approval"
    ),
]