# PostgreSQL database design

The detailed Django model implementation will be added module by module. Core relationships:

- `User` has a `Role`; users may create invoices, approve assigned invoices, and perform payments according to permissions.
- `Vendor` has many `VendorBankDetail` and `VendorOnboarding` records.
- `Invoice` belongs to a vendor and has many `InvoiceLineItem`, `InvoiceAttachment`, `InvoiceValidation`, `InvoiceMatching`, `InvoiceApproval`, `Payment`, and `AuditLog` records.
- `PurchaseOrder` belongs to a vendor and has many `PurchaseOrderLineItem`.
- `GoodsReceiptNote` belongs to a purchase order and has many `GoodsReceiptNoteLineItem`.
- `InvoiceMatching` links an invoice to a PO and optionally a GRN.
- `ApprovalWorkflow` has ordered/parallel `ApprovalStep` records; invoice-level decisions are recorded in `InvoiceApproval`.
- `Payment` belongs to an invoice and may have one or more `PaymentAdvice` records.
- `Notification` belongs to a recipient user; `AuditLog` records actor, action, related object, before/after values, timestamp, and comments.

## Initial entities and important constraints

| Entity | Important fields / constraints |
|---|---|
| User | username/email unique, password hash, role, active flag |
| Role | unique role code/name |
| Vendor | unique vendor code, GSTIN, TIN, contact and status |
| VendorBankDetail | vendor FK, bank name, account number, IFSC; access restricted |
| VendorOnboarding | vendor FK, submitted data, status, reviewed_by |
| Invoice | vendor FK, invoice number, invoice date, due date, PO number, currency, subtotal, tax, total, status, uploaded_by |
| InvoiceLineItem | invoice FK, description, item code, quantity, unit price, tax %, tax amount, line total |
| InvoiceAttachment | invoice FK, file, original name, MIME type, size, OCR status |
| PurchaseOrder | vendor FK, PO number unique, dates, status, total |
| PurchaseOrderLineItem | PO FK, description, item code, quantity, unit price, tax, total |
| GoodsReceiptNote | PO FK, GRN number unique, received date, status |
| GoodsReceiptNoteLineItem | GRN FK, PO line FK, received quantity |
| InvoiceValidation | invoice FK, rule code, result, message, details |
| InvoiceMatching | invoice FK, PO FK, optional GRN FK, match type, result, tolerance |
| ApprovalWorkflow | name, enabled, amount bounds, conditions |
| ApprovalStep | workflow FK, step order, approver role/user, parallel group |
| InvoiceApproval | invoice FK, step FK, approver FK, decision, comments, decision time |
| Payment | invoice FK, amount, method, reference, date, status |
| PaymentAdvice | payment FK, advice number, generated file, sent timestamp |
| Notification | recipient FK, type, message, read timestamp |
| AuditLog | actor FK, action, object type/id, previous/updated JSON, comments, timestamp |

Use `DecimalField` for currency, foreign keys with explicit deletion behavior, indexes for common filtering fields, and unique constraints such as `(vendor, invoice_number)` to prevent duplicate vendor invoices.
