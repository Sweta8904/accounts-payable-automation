
from django.urls import path

from .views import InvoiceListCreateView, InvoiceDetailView


urlpatterns = [
    path("", InvoiceListCreateView.as_view(), name="invoice-list-create"),
    path("<int:pk>/", InvoiceDetailView.as_view(), name="invoice-detail"),
]
