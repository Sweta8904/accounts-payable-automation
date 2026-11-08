
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    PurchaseOrderViewSet,
    GoodsReceiptNoteViewSet,
    InvoiceMatchingView,
)

router = DefaultRouter()

router.register(
    "purchase-orders",
    PurchaseOrderViewSet,
    basename="purchase-orders"
)

router.register(
    "grns",
    GoodsReceiptNoteViewSet,
    basename="grns"
)

urlpatterns = [
    path(
        "invoices/<int:invoice_id>/match/",
        InvoiceMatchingView.as_view(),
        name="invoice-match"
    ),
] + router.urls
