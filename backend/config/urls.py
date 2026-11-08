
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

# Backend home page
def home(request):
    return JsonResponse({
        "project": "Accounts Payable Automation",
        "status": "running",
        "message": "Welcome to Accounts Payable Automation API"
    })


# Health check API
def health(request):
    return JsonResponse({
        "status": "ok",
        "service": "accounts-payable-api"
    })


urlpatterns = [
    # Home
    path("", home, name="home"),

    # Django Admin
    path("admin/", admin.site.urls),

    # Health Check
    path("api/health/", health, name="health"),

    # Invoice API
    path("api/invoices/", include("invoices.urls")),
     path("api/auth/", include("accounts.urls")),
path("api/reports/", include("apps.reports.urls")),
path("api/audit-logs/", include("apps.audit_logs.urls")),

path("api/payments/", include("apps.payments.urls")),

    path("api/vendors/", include("apps.vendors.urls")),
    path("api/", include("apps.purchase_orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )