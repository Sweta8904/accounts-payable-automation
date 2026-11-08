from django.urls import path
from .views import ReportsSummaryView

urlpatterns = [
    path("summary/", ReportsSummaryView.as_view(), name="reports-summary"),
]