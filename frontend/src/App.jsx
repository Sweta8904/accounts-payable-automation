
import { useEffect, useState } from 'react'
import { NavLink, Routes, Route } from 'react-router-dom'
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const navItems = [
  ['/', 'Dashboard'],
  ['/invoices', 'Invoices'],
  ['/upload', 'Invoice Upload'],
  ['/approvals', 'Approvals'],
  ['/vendors', 'Vendors'],
  ['/purchase-orders', 'Purchase Orders'],
  ['/grn', 'Goods Receipt Notes'],
  ['/payments', 'Payments'],
  ['/reports', 'Reports'],
  ['/audit-logs', 'Audit Logs'],
  ['/settings', 'Settings'],
]

function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/auth/token/', {
        username,
        password,
      })

      localStorage.setItem('access_token', response.data.access)
      if (response.data.refresh) {
        localStorage.setItem('refresh_token', response.data.refresh)
      }
      onLogin(response.data.access)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Login failed. Check your username and password.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <div className="brand-mark login-mark">AP</div>
        <h1>AP Flow</h1>
        <p className="muted">Accounts Payable Automation</p>

        <label>Username</label>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter username"
          required
        />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter password"
          required
        />

        {error && <div className="error-message">{error}</div>}

        <button className="primary-button" disabled={loading}>
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </div>
  )
}

function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/invoices/dashboard/')
      .then((res) => setData(res.data.dashboard))
      .catch((err) => {
        setError(err.response?.data?.detail || 'Could not load dashboard.')
      })
      .finally(() => setLoading(false))
  }, [])

  const metrics = [
    ['Total Invoices', data?.total_invoices ?? 0, 'All uploaded invoices'],
    ['Pending Approvals', data?.pending ?? 0, 'Awaiting approval'],
    ['Approved Invoices', data?.approved ?? 0, 'Successfully approved'],
    ['Rejected Invoices', data?.rejected ?? 0, 'Rejected invoices'],
    ['Uploaded', data?.uploaded ?? 0, 'Awaiting processing'],
    ['Validation Failed', data?.validation_failed ?? 0, 'Require attention'],
  ]

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">OVERVIEW</p>
          <h1>Accounts Payable Dashboard</h1>
          <p className="muted">
            Monitor invoice processing, approvals, and payments.
          </p>
        </div>
        <button className="secondary-button" onClick={() => window.location.reload()}>
          Refresh
        </button>
      </div>

      {loading && <p className="muted mt-4">Loading dashboard data...</p>}
      {error && <div className="error-message mt-4">{error}</div>}

      {!loading && data && (
        <>
          <div className="row g-3 mt-3">
            {metrics.map(([label, value, description]) => (
              <div className="col-12 col-sm-6 col-xl-4" key={label}>
                <div className="metric-card">
                  <span>{label}</span>
                  <strong>{value}</strong>
                  <small>{description}</small>
                </div>
              </div>
            ))}
          </div>

          <div className="row g-3 mt-2">
            <div className="col-12 col-md-4">
              <div className="amount-card">
                <span>Total Invoice Amount</span>
                <strong>₹{Number(data.total_amount).toLocaleString('en-IN')}</strong>
              </div>
            </div>
            <div className="col-12 col-md-4">
              <div className="amount-card">
                <span>Pending Amount</span>
                <strong>₹{Number(data.pending_amount).toLocaleString('en-IN')}</strong>
              </div>
            </div>
            <div className="col-12 col-md-4">
              <div className="amount-card">
                <span>Approved Amount</span>
                <strong>₹{Number(data.approved_amount).toLocaleString('en-IN')}</strong>
              </div>
            </div>
          </div>
        </>
      )}
    </section>
  )
}

function Invoices() {
  const [invoices, setInvoices] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/invoices/')
      .then((res) => setInvoices(res.data.invoices || []))
      .catch((err) => {
        setError(err.response?.data?.detail || 'Could not load invoices.')
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">WORKSPACE</p>
          <h1>Invoices</h1>
          <p className="muted">View and monitor uploaded invoices.</p>
        </div>
      </div>

      {loading && <p className="muted mt-4">Loading invoices...</p>}
      {error && <div className="error-message mt-4">{error}</div>}

      {!loading && !error && (
        <div className="table-card mt-4">
          <div className="table-responsive">
            <table className="table align-middle mb-0">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Invoice Number</th>
                  <th>Vendor</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Validation</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((invoice) => (
                  <tr key={invoice.id}>
                    <td>{invoice.id}</td>
                    <td>{invoice.invoice_number || '—'}</td>
                    <td>{invoice.vendor_name || '—'}</td>
                    <td>₹{Number(invoice.total_amount).toLocaleString('en-IN')}</td>
                    <td>
                      <span className={`status-badge ${String(invoice.status).toLowerCase()}`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td>{invoice.validation_status}</td>
                  </tr>
                ))}
                {invoices.length === 0 && (
                  <tr><td colSpan="6" className="text-center py-4">No invoices found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  )
}



function InvoiceUpload() {
  const [file, setFile] = useState(null)
  const [invoiceNumber, setInvoiceNumber] = useState('')
  const [vendorName, setVendorName] = useState('')
  const [invoiceDate, setInvoiceDate] = useState('')
  const [totalAmount, setTotalAmount] = useState('')
  const [taxAmount, setTaxAmount] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleUpload(e) {
    e.preventDefault()
    setMessage('')
    setError('')

    if (!file) {
      setError('Please select an invoice file.')
      return
    }

    const formData = new FormData()
    formData.append('invoice_file', file)

    if (invoiceNumber) formData.append('invoice_number', invoiceNumber)
    if (vendorName) formData.append('vendor_name', vendorName)
    if (invoiceDate) formData.append('invoice_date', invoiceDate)
    if (totalAmount) formData.append('total_amount', totalAmount)
    if (taxAmount) formData.append('tax_amount', taxAmount)

    setLoading(true)

    try {
      const response = await api.post('/invoices/', formData)
      const result = response.data

      if (result.status === 'success') {
        setMessage(
          `Invoice uploaded successfully. OCR and validation completed. Invoice ID: ${result.invoice.id}. Validation: ${result.validation?.valid ? 'Passed' : 'Needs review'}.`
        )
      } else {
        setMessage(
          `Invoice uploaded, but processing needs attention. Invoice ID: ${result.invoice?.id}.`
        )
      }

      setFile(null)
      setInvoiceNumber('')
      setVendorName('')
      setInvoiceDate('')
      setTotalAmount('')
      setTaxAmount('')

      e.target.reset()
    } catch (err) {
      const details = err.response?.data?.errors
      setError(
        typeof details === 'object'
          ? JSON.stringify(details)
          : err.response?.data?.message ||
            err.response?.data?.detail ||
            'Upload failed. Please check the file and try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">INVOICE MANAGEMENT</p>
          <h1>Upload Invoice</h1>
          <p className="muted">
            Upload a PDF or image. Django will extract text and validate the invoice.
          </p>
        </div>
      </div>

      <form className="upload-card mt-4" onSubmit={handleUpload}>
        <div className="upload-file-area">
          <div className="upload-icon">↑</div>
          <h3>Select Invoice Document</h3>
          <p>Supported formats: PDF, JPG, JPEG and PNG. Maximum 10 MB.</p>
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            required
          />
          {file && <p className="selected-file">Selected: {file.name}</p>}
        </div>

        <h3 className="form-section-title">Invoice Details</h3>
        <p className="muted mb-3">
          These fields are optional if the information is available in the document.
        </p>

        <div className="row g-3">
          <div className="col-md-6">
            <label className="field-label">Invoice Number</label>
            <input
              className="form-control"
              value={invoiceNumber}
              onChange={(e) => setInvoiceNumber(e.target.value)}
              placeholder="Example: INV-1004"
            />
          </div>

          <div className="col-md-6">
            <label className="field-label">Vendor Name</label>
            <input
              className="form-control"
              value={vendorName}
              onChange={(e) => setVendorName(e.target.value)}
              placeholder="Enter vendor name"
            />
          </div>

          <div className="col-md-4">
            <label className="field-label">Invoice Date</label>
            <input
              type="date"
              className="form-control"
              value={invoiceDate}
              onChange={(e) => setInvoiceDate(e.target.value)}
            />
          </div>

          <div className="col-md-4">
            <label className="field-label">Total Amount</label>
            <input
              type="number"
              min="0"
              step="0.01"
              className="form-control"
              value={totalAmount}
              onChange={(e) => setTotalAmount(e.target.value)}
              placeholder="0.00"
            />
          </div>

          <div className="col-md-4">
            <label className="field-label">Tax Amount</label>
            <input
              type="number"
              min="0"
              step="0.01"
              className="form-control"
              value={taxAmount}
              onChange={(e) => setTaxAmount(e.target.value)}
              placeholder="0.00"
            />
          </div>
        </div>

        {message && <div className="success-message mt-3">{message}</div>}
        {error && <div className="error-message mt-3">{error}</div>}

        <button className="primary-button upload-submit" disabled={loading}>
          {loading ? 'Uploading and processing...' : 'Upload Invoice & Run OCR'}
        </button>
      </form>
    </section>
  )
}

function Approvals() {
  const [invoices, setInvoices] = useState([])
  const [comments, setComments] = useState({})
  const [loading, setLoading] = useState(true)
  const [processingId, setProcessingId] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function loadInvoices() {
    setLoading(true)
    setError('')

    try {
      const response = await api.get('/invoices/')
      setInvoices(
        (response.data.invoices || []).filter(
          (invoice) => invoice.status === 'PENDING'
        )
      )
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Could not load pending invoices.'
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadInvoices()
  }, [])

  async function processInvoice(invoiceId, action) {
    setMessage('')
    setError('')

    const comment = comments[invoiceId] || ''

    if (action === 'REJECTED' && !comment.trim()) {
      setError('Please enter a rejection reason.')
      return
    }

    setProcessingId(invoiceId)

    try {
      const response = await api.post(`/invoices/${invoiceId}/approval/`, {
        action,
        comments: comment,
      })

      setMessage(response.data.message)
      setComments((previous) => {
        const updated = { ...previous }
        delete updated[invoiceId]
        return updated
      })

      await loadInvoices()
    } catch (err) {
      setError(
        err.response?.data?.message ||
        err.response?.data?.detail ||
        'Could not process this invoice.'
      )
    } finally {
      setProcessingId(null)
    }
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">FINANCE WORKFLOW</p>
          <h1>Invoice Approvals</h1>
          <p className="muted">
            Review validated invoices and record approval decisions.
          </p>
        </div>

        <button className="secondary-button" onClick={loadInvoices}>
          Refresh
        </button>
      </div>

      {message && <div className="success-message mt-4">{message}</div>}
      {error && <div className="error-message mt-4">{error}</div>}
      {loading && <p className="muted mt-4">Loading pending invoices...</p>}

      {!loading && invoices.length === 0 && (
        <div className="empty-state mt-4">
          <h3>No pending invoices</h3>
          <p>There are currently no invoices awaiting approval.</p>
        </div>
      )}

      {!loading && invoices.map((invoice) => (
        <div className="approval-card mt-4" key={invoice.id}>
          <div className="approval-header">
            <div>
              <h3>{invoice.invoice_number || `Invoice #${invoice.id}`}</h3>
              <p>{invoice.vendor_name || 'Unknown vendor'}</p>
            </div>
            <span className={`status-badge ${invoice.validation_status === 'VALID' ? 'approved' : 'rejected'}`}>
              {invoice.validation_status}
            </span>
          </div>

          <div className="approval-details">
            <div>
              <span>Invoice Amount</span>
              <strong>₹{Number(invoice.total_amount).toLocaleString('en-IN')}</strong>
            </div>
            <div>
              <span>Invoice Date</span>
              <strong>{invoice.invoice_date || 'Not available'}</strong>
            </div>
            <div>
              <span>Validation</span>
              <strong>{invoice.validation_status}</strong>
            </div>
          </div>

          {invoice.validation_message && (
            <p className="validation-note">{invoice.validation_message}</p>
          )}

          <label className="field-label">Comments / Rejection Reason</label>
          <textarea
            className="form-control"
            rows="2"
            placeholder="Enter comments. Required when rejecting."
            value={comments[invoice.id] || ''}
            onChange={(e) =>
              setComments((previous) => ({
                ...previous,
                [invoice.id]: e.target.value,
              }))
            }
          />

          <div className="approval-actions">
            <button
              className="approve-button"
              disabled={processingId === invoice.id || invoice.validation_status !== 'VALID'}
              onClick={() => processInvoice(invoice.id, 'APPROVED')}
            >
              {processingId === invoice.id ? 'Processing...' : 'Approve'}
            </button>

            <button
              className="reject-button"
              disabled={processingId === invoice.id}
              onClick={() => processInvoice(invoice.id, 'REJECTED')}
            >
              Reject
            </button>
          </div>

          {invoice.validation_status !== 'VALID' && (
            <p className="muted mt-2">
              Approval is disabled until invoice validation passes. You can still reject it.
            </p>
          )}

          <button
            className="history-button"
            onClick={async () => {
              try {
                const response = await api.get(`/invoices/${invoice.id}/approval/`)
                const history = response.data.history || []
                window.alert(
                  history.length
                    ? history.map((item) =>
                        `${item.action} by ${item.performed_by || 'Unknown'}\n${item.comments || ''}\n${item.created_at}`
                      ).join('\n\n')
                    : 'No approval history yet.'
                )
              } catch (err) {
                window.alert(
                  err.response?.data?.detail || 'Could not load approval history.'
                )
              }
            }}
          >
            View Approval History
          </button>
        </div>
      ))}
    </section>
  )
}


function getRows(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.invoices)) return data.invoices;
  return [];
}

function ApiError({ error }) {
  return error ? <div className="error-message mt-3">{error}</div> : null;
}

function Vendors() {
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState({
    vendor_code: "", name: "", email: "", phone: "",
    address: "", tax_number: "", payment_terms: "Net 30",
    is_active: true
  });
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    try {
      setRows(getRows((await api.get("/vendors/")).data));
    } catch (e) {
      setError(e.response?.data?.detail || "Unable to load vendors.");
    }
  }

  useEffect(() => { load(); }, []);

  function change(e) {
    const { name, value, type, checked } = e.target;
    setForm(p => ({ ...p, [name]: type === "checkbox" ? checked : value }));
  }

  async function save(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      if (editing) {
        await api.patch(`/vendors/${editing}/`, form);
      } else {
        await api.post("/vendors/", form);
      }
      setForm({
        vendor_code: "", name: "", email: "", phone: "",
        address: "", tax_number: "", payment_terms: "Net 30",
        is_active: true
      });
      setEditing(null);
      await load();
    } catch (e) {
      setError(JSON.stringify(e.response?.data || "Unable to save vendor."));
    } finally {
      setLoading(false);
    }
  }

  function edit(row) {
    setEditing(row.id);
    setForm({
      vendor_code: row.vendor_code || "",
      name: row.name || "",
      email: row.email || "",
      phone: row.phone || "",
      address: row.address || "",
      tax_number: row.tax_number || "",
      payment_terms: row.payment_terms || "Net 30",
      is_active: row.is_active
    });
  }

  async function remove(id) {
    if (!window.confirm("Delete this vendor?")) return;
    try {
      await api.delete(`/vendors/${id}/`);
      await load();
    } catch (e) {
      setError(e.response?.data?.detail || "Could not delete vendor. It may be linked to a purchase order.");
    }
  }

  return (
    <section>
      <div className="page-heading">
        <div><p className="eyebrow">WORKSPACE</p><h1>Vendors</h1>
          <p className="muted">Manage supplier information.</p></div>
        <button className="secondary-button" onClick={load}>Refresh</button>
      </div>

      <form className="upload-card mt-4" onSubmit={save}>
        <h3>{editing ? "Edit Vendor" : "Add Vendor"}</h3>
        <div className="row g-3">
          {[
            ["vendor_code", "Vendor Code"],
            ["name", "Vendor Name"],
            ["email", "Email"],
            ["phone", "Phone"],
            ["tax_number", "Tax / GST Number"],
            ["payment_terms", "Payment Terms"]
          ].map(([name, label]) => (
            <div className="col-md-6" key={name}>
              <label className="field-label">{label}</label>
              <input className="form-control" name={name}
                value={form[name]} onChange={change} required={["vendor_code", "name"].includes(name)} />
            </div>
          ))}
          <div className="col-12">
            <label className="field-label">Address</label>
            <textarea className="form-control" name="address"
              value={form.address} onChange={change} rows="2" />
          </div>
          <div className="col-12">
            <label><input type="checkbox" name="is_active"
              checked={form.is_active} onChange={change} /> Active vendor</label>
          </div>
        </div>
        <ApiError error={error} />
        <div className="d-flex gap-2 mt-3">
          <button className="primary-button" disabled={loading}>
            {loading ? "Saving..." : editing ? "Update Vendor" : "Add Vendor"}
          </button>
          {editing && <button type="button" className="secondary-button"
            onClick={() => { setEditing(null); setForm({
              vendor_code: "", name: "", email: "", phone: "",
              address: "", tax_number: "", payment_terms: "Net 30", is_active: true
            }); }}>Cancel</button>}
        </div>
      </form>

      <div className="table-card mt-4 table-responsive">
        <table className="table align-middle mb-0">
          <thead><tr><th>Code</th><th>Vendor</th><th>Email</th><th>Phone</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {rows.map(v => <tr key={v.id}>
              <td>{v.vendor_code}</td><td>{v.name}</td><td>{v.email || "—"}</td>
              <td>{v.phone || "—"}</td><td>{v.is_active ? "Active" : "Inactive"}</td>
              <td><button className="secondary-button me-2" onClick={() => edit(v)}>Edit</button>
                <button className="reject-button" onClick={() => remove(v.id)}>Delete</button></td>
            </tr>)}
            {!rows.length && <tr><td colSpan="6" className="text-center">No vendors found.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function PurchaseOrders() {
  const [rows, setRows] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    po_number: "", vendor: "", order_date: new Date().toISOString().slice(0, 10),
    expected_delivery_date: "", status: "APPROVED", currency: "INR",
    notes: "", items: [{ description: "", quantity: 1, unit_price: 0, tax_rate: 18 }]
  });

  async function load() {
    try {
      const [p, v] = await Promise.all([api.get("/purchase-orders/"), api.get("/vendors/")]);
      setRows(getRows(p.data));
      setVendors(getRows(v.data));
    } catch (e) {
      setError(e.response?.data?.detail || "Unable to load purchase orders.");
    }
  }

  useEffect(() => { load(); }, []);

  function updateItem(index, key, value) {
    setForm(p => ({
      ...p,
      items: p.items.map((item, i) => i === index
        ? { ...item, [key]: value } : item)
    }));
  }

  async function save(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/purchase-orders/", {
        ...form,
        vendor: Number(form.vendor),
        items: form.items.map(i => ({
          ...i, quantity: Number(i.quantity),
          unit_price: Number(i.unit_price), tax_rate: Number(i.tax_rate)
        }))
      });
      setForm(p => ({
        ...p, po_number: "", vendor: "", expected_delivery_date: "",
        notes: "", items: [{ description: "", quantity: 1, unit_price: 0, tax_rate: 18 }]
      }));
      await load();
    } catch (e) {
      setError(JSON.stringify(e.response?.data || "Unable to create purchase order."));
    }
  }

  return (
    <section>
      <div className="page-heading"><div><p className="eyebrow">WORKSPACE</p>
        <h1>Purchase Orders</h1><p className="muted">Create and monitor purchase orders.</p></div>
        <button className="secondary-button" onClick={load}>Refresh</button></div>

      <form className="upload-card mt-4" onSubmit={save}>
        <h3>Create Purchase Order</h3>
        <div className="row g-3">
          <div className="col-md-6"><label className="field-label">PO Number</label>
            <input className="form-control" required value={form.po_number}
              onChange={e => setForm(p => ({ ...p, po_number: e.target.value }))} /></div>
          <div className="col-md-6"><label className="field-label">Vendor</label>
            <select className="form-select" required value={form.vendor}
              onChange={e => setForm(p => ({ ...p, vendor: e.target.value }))}>
              <option value="">Select vendor</option>
              {vendors.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
            </select></div>
          <div className="col-md-6"><label className="field-label">Order Date</label>
            <input type="date" className="form-control" required value={form.order_date}
              onChange={e => setForm(p => ({ ...p, order_date: e.target.value }))} /></div>
          <div className="col-md-6"><label className="field-label">Expected Delivery</label>
            <input type="date" className="form-control" value={form.expected_delivery_date}
              onChange={e => setForm(p => ({ ...p, expected_delivery_date: e.target.value }))} /></div>
        </div>

        <h4 className="form-section-title mt-4">Order Items</h4>
        {form.items.map((item, i) => <div className="row g-2 mb-2" key={i}>
          <div className="col-md-5"><input className="form-control" placeholder="Description" required
            value={item.description} onChange={e => updateItem(i, "description", e.target.value)} /></div>
          <div className="col-4 col-md-2"><input className="form-control" type="number" min="0.01" step="0.01" placeholder="Qty"
            value={item.quantity} onChange={e => updateItem(i, "quantity", e.target.value)} /></div>
          <div className="col-4 col-md-2"><input className="form-control" type="number" min="0" step="0.01" placeholder="Unit price"
            value={item.unit_price} onChange={e => updateItem(i, "unit_price", e.target.value)} /></div>
          <div className="col-4 col-md-2"><input className="form-control" type="number" min="0" step="0.01" placeholder="Tax %"
            value={item.tax_rate} onChange={e => updateItem(i, "tax_rate", e.target.value)} /></div>
          <div className="col-md-1"><button type="button" className="reject-button"
            onClick={() => setForm(p => ({ ...p, items: p.items.filter((_, n) => n !== i) }))}
            disabled={form.items.length === 1}>×</button></div>
        </div>)}
        <button type="button" className="secondary-button mt-2"
          onClick={() => setForm(p => ({ ...p, items: [...p.items, { description: "", quantity: 1, unit_price: 0, tax_rate: 18 }] }))}>
          + Add Item
        </button>
        <div className="mt-3"><label className="field-label">Notes</label>
          <textarea className="form-control" rows="2" value={form.notes}
            onChange={e => setForm(p => ({ ...p, notes: e.target.value }))} /></div>
        <ApiError error={error} />
        <button className="primary-button mt-3">Create Purchase Order</button>
      </form>

      <div className="table-card mt-4 table-responsive">
        <table className="table align-middle mb-0">
          <thead><tr><th>PO Number</th><th>Vendor</th><th>Order Date</th><th>Status</th><th>Subtotal</th></tr></thead>
          <tbody>{rows.map(p => <tr key={p.id}><td>{p.po_number}</td><td>{p.vendor_name}</td>
            <td>{p.order_date}</td><td>{p.status}</td><td>₹{Number(p.total_amount || 0).toLocaleString("en-IN")}</td></tr>)}
            {!rows.length && <tr><td colSpan="5" className="text-center">No purchase orders found.</td></tr>}</tbody>
        </table>
      </div>
    </section>
  );
}

function GoodsReceipts() {
  const [orders, setOrders] = useState([]);
  const [selected, setSelected] = useState("");
  const [rows, setRows] = useState([]);
  const [grns, setGrns] = useState([]);
  const [grnNumber, setGrnNumber] = useState("");
  const [error, setError] = useState("");

  async function load() {
    try {
      const [p, g] = await Promise.all([api.get("/purchase-orders/"), api.get("/grns/")]);
      setOrders(getRows(p.data));
      setGrns(getRows(g.data));
    } catch (e) {
      setError(e.response?.data?.detail || "Unable to load GRNs.");
    }
  }

  useEffect(() => { load(); }, []);

  function selectOrder(id) {
    setSelected(id);
    const po = orders.find(p => String(p.id) === String(id));
    setRows((po?.items || []).map(item => ({
      purchase_order_item: item.id,
      description: item.description,
      received_quantity: item.quantity,
      accepted_quantity: item.quantity,
      notes: ""
    })));
  }

  function updateRow(index, key, value) {
    setRows(p => p.map((r, i) => i === index ? { ...r, [key]: value } : r));
  }

  async function save(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/grns/", {
        grn_number: grnNumber,
        purchase_order: Number(selected),
        received_date: new Date().toISOString().slice(0, 10),
        status: "RECEIVED",
        notes: "Goods receipt recorded through AP Flow",
        items: rows.map(r => ({
          ...r,
          received_quantity: Number(r.received_quantity),
          accepted_quantity: Number(r.accepted_quantity)
        }))
      });
      setGrnNumber("");
      setSelected("");
      setRows([]);
      await load();
    } catch (e) {
      setError(JSON.stringify(e.response?.data || "Unable to create GRN."));
    }
  }

  return (
    <section>
      <div className="page-heading"><div><p className="eyebrow">WORKSPACE</p>
        <h1>Goods Receipt Notes</h1><p className="muted">Record goods received against purchase orders.</p></div>
        <button className="secondary-button" onClick={load}>Refresh</button></div>

      <form className="upload-card mt-4" onSubmit={save}>
        <h3>Record Goods Receipt</h3>
        <div className="row g-3">
          <div className="col-md-6"><label className="field-label">GRN Number</label>
            <input className="form-control" required value={grnNumber} onChange={e => setGrnNumber(e.target.value)} /></div>
          <div className="col-md-6"><label className="field-label">Purchase Order</label>
            <select className="form-select" required value={selected} onChange={e => selectOrder(e.target.value)}>
              <option value="">Select purchase order</option>
              {orders.map(p => <option key={p.id} value={p.id}>{p.po_number} — {p.vendor_name}</option>)}
            </select></div>
        </div>
        {rows.map((r, i) => <div className="row g-2 mt-2" key={r.purchase_order_item}>
          <div className="col-12"><strong>{r.description}</strong></div>
          <div className="col-6 col-md-4"><label className="field-label">Received Qty</label>
            <input className="form-control" type="number" min="0" step="0.01" value={r.received_quantity}
              onChange={e => updateRow(i, "received_quantity", e.target.value)} /></div>
          <div className="col-6 col-md-4"><label className="field-label">Accepted Qty</label>
            <input className="form-control" type="number" min="0" step="0.01" value={r.accepted_quantity}
              onChange={e => updateRow(i, "accepted_quantity", e.target.value)} /></div>
          <div className="col-12 col-md-4"><label className="field-label">Notes</label>
            <input className="form-control" value={r.notes} onChange={e => updateRow(i, "notes", e.target.value)} /></div>
        </div>)}
        <ApiError error={error} />
        <button className="primary-button mt-3" disabled={!selected || !rows.length}>Save Goods Receipt</button>
      </form>

      <div className="table-card mt-4 table-responsive"><table className="table mb-0">
        <thead><tr><th>GRN</th><th>PO</th><th>Received Date</th><th>Status</th></tr></thead>
        <tbody>{grns.map(g => <tr key={g.id}><td>{g.grn_number}</td><td>{g.po_number}</td>
          <td>{g.received_date}</td><td>{g.status}</td></tr>)}
          {!grns.length && <tr><td colSpan="4" className="text-center">No goods receipts found.</td></tr>}</tbody>
      </table></div>
    </section>
  );
}

function Payments() {
  const [rows, setRows] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [form, setForm] = useState({
    invoice: "", payment_reference: "", amount: "",
    payment_date: new Date().toISOString().slice(0, 10),
    payment_method: "BANK_TRANSFER", status: "PENDING", notes: ""
  });
  const [error, setError] = useState("");

  async function load() {
    try {
      const [p, i] = await Promise.all([api.get("/payments/"), api.get("/invoices/")]);
      setRows(getRows(p.data));
      setInvoices(getRows(i.data).filter(x => ["APPROVED", "PAID"].includes(x.status)));
    } catch (e) {
      setError(e.response?.data?.detail || "Unable to load payments.");
    }
  }

  useEffect(() => { load(); }, []);

  async function save(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/payments/", {
        ...form, invoice: Number(form.invoice), amount: Number(form.amount)
      });
      setForm(p => ({ ...p, invoice: "", payment_reference: "", amount: "", notes: "" }));
      await load();
    } catch (e) {
      setError(JSON.stringify(e.response?.data || "Unable to record payment."));
    }
  }

  async function complete(id) {
    if (!window.confirm("Mark this payment as completed?")) return;
    try {
      await api.patch(`/payments/${id}/`, { status: "COMPLETED" });
      await load();
    } catch (e) {
      setError(JSON.stringify(e.response?.data || "Unable to update payment."));
    }
  }

  return (
    <section>
      <div className="page-heading"><div><p className="eyebrow">WORKSPACE</p>
        <h1>Payments</h1><p className="muted">Track payment records for approved and matched invoices.</p></div>
        <button className="secondary-button" onClick={load}>Refresh</button></div>

      <form className="upload-card mt-4" onSubmit={save}>
        <h3>Record Payment</h3>
        <div className="row g-3">
          <div className="col-md-6"><label className="field-label">Approved Invoice</label>
            <select className="form-select" required value={form.invoice}
              onChange={e => setForm(p => ({ ...p, invoice: e.target.value }))}>
              <option value="">Select invoice</option>
              {invoices.map(i => <option key={i.id} value={i.id}>{i.invoice_number} — {i.vendor_name} — ₹{i.total_amount}</option>)}
            </select></div>
          <div className="col-md-6"><label className="field-label">Payment Reference</label>
            <input className="form-control" required value={form.payment_reference}
              onChange={e => setForm(p => ({ ...p, payment_reference: e.target.value }))} /></div>
          <div className="col-md-4"><label className="field-label">Amount</label>
            <input className="form-control" type="number" min="0.01" step="0.01" required value={form.amount}
              onChange={e => setForm(p => ({ ...p, amount: e.target.value }))} /></div>
          <div className="col-md-4"><label className="field-label">Payment Date</label>
            <input className="form-control" type="date" required value={form.payment_date}
              onChange={e => setForm(p => ({ ...p, payment_date: e.target.value }))} /></div>
          <div className="col-md-4"><label className="field-label">Method</label>
            <select className="form-select" value={form.payment_method}
              onChange={e => setForm(p => ({ ...p, payment_method: e.target.value }))}>
              <option value="BANK_TRANSFER">Bank Transfer</option><option value="UPI">UPI</option><option value="CHEQUE">Cheque</option></select></div>
        </div>
        <ApiError error={error} />
        <button className="primary-button mt-3">Record Payment</button>
        <p className="muted mt-2">Payment records only. No bank transfer is initiated by this application.</p>
      </form>

      <div className="table-card mt-4 table-responsive"><table className="table align-middle mb-0">
        <thead><tr><th>Reference</th><th>Invoice</th><th>Amount</th><th>Date</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>{rows.map(p => <tr key={p.id}><td>{p.payment_reference}</td><td>{p.invoice_number}</td>
          <td>₹{Number(p.amount).toLocaleString("en-IN")}</td><td>{p.payment_date}</td><td>{p.status}</td>
          <td>{p.status === "PENDING" && <button className="approve-button" onClick={() => complete(p.id)}>Mark Completed</button>}</td></tr>)}
          {!rows.length && <tr><td colSpan="6" className="text-center">No payments found.</td></tr>}</tbody>
      </table></div>
    </section>
  );
}

function Reports() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    try {
      setData((await api.get("/reports/summary/")).data);
      setError("");
    } catch (e) {
      setError(e.response?.data?.detail || "Unable to load reports.");
    }
  }

  useEffect(() => { load(); }, []);

  const money = value => `₹${Number(value || 0).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;

  return (
    <section>
      <div className="page-heading"><div><p className="eyebrow">ANALYTICS</p>
        <h1>Reports</h1><p className="muted">Live financial and operational summary.</p></div>
        <button className="secondary-button" onClick={load}>Refresh</button></div>
      <ApiError error={error} />
      {data && <>
        <div className="row g-3 mt-3">
          {[
            ["Total Invoices", data.invoices?.total_count],
            ["Invoice Amount", money(data.invoices?.total_amount)],
            ["Tax Amount", money(data.invoices?.tax_amount)],
            ["Completed Payments", money(data.payments?.completed_amount)],
            ["Active Vendors", data.vendors?.active],
            ["Overdue Invoices", data.overdue_invoices?.count]
          ].map(([label, value]) => <div className="col-12 col-sm-6 col-xl-4" key={label}>
            <div className="metric-card"><span>{label}</span><strong>{value ?? 0}</strong></div>
          </div>)}
        </div>
        <div className="table-card mt-4 table-responsive"><h3 className="p-3 mb-0">Invoice Status Summary</h3>
          <table className="table mb-0"><thead><tr><th>Status</th><th>Count</th><th>Amount</th></tr></thead>
            <tbody>{(data.invoices?.by_status || []).map(x => <tr key={x.status}><td>{x.status}</td><td>{x.count}</td><td>{money(x.amount)}</td></tr>)}</tbody>
          </table></div>
        <div className="table-card mt-4 table-responsive"><h3 className="p-3 mb-0">Purchase Order Status</h3>
          <table className="table mb-0"><thead><tr><th>Status</th><th>Count</th></tr></thead>
            <tbody>{(data.purchase_orders?.by_status || []).map(x => <tr key={x.status}><td>{x.status}</td><td>{x.count}</td></tr>)}</tbody>
          </table></div>
      </>}
    </section>
  );
}

function AuditLogs() {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  async function load() {
    try {
      const response = await api.get("/audit-logs/", { params: search ? { search } : {} });
      setRows(getRows(response.data));
      setError("");
    } catch (e) {
      setError(e.response?.data?.detail || "Unable to load audit logs. Admin access may be required.");
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <section>
      <div className="page-heading"><div><p className="eyebrow">SECURITY & COMPLIANCE</p>
        <h1>Audit Logs</h1><p className="muted">Review recorded user and payment activities.</p></div>
        <button className="secondary-button" onClick={load}>Refresh</button></div>
      <div className="d-flex gap-2 mt-4">
        <input className="form-control" placeholder="Search description, user or record ID"
          value={search} onChange={e => setSearch(e.target.value)} />
        <button className="primary-button" onClick={load}>Search</button>
      </div>
      <ApiError error={error} />
      <div className="table-card mt-3 table-responsive"><table className="table align-middle mb-0">
        <thead><tr><th>Date</th><th>User</th><th>Action</th><th>Entity</th><th>Record ID</th><th>Description</th></tr></thead>
        <tbody>{rows.map(log => <tr key={log.id}><td>{new Date(log.created_at).toLocaleString()}</td>
          <td>{log.username || "System"}</td><td>{log.action}</td><td>{log.entity_type}</td>
          <td>{log.entity_id}</td><td>{log.description}</td></tr>)}
          {!rows.length && !error && <tr><td colSpan="6" className="text-center">No audit records found.</td></tr>}</tbody>
      </table></div>
    </section>
  );
}

function Settings() {
  const [settings, setSettings] = useState(() => {
  const saved = localStorage.getItem("ap_app_settings");

  return saved
    ? JSON.parse(saved)
    : {
        companyName: "Templegate Technologies",
        currency: "INR",
        dateFormat: "DD-MM-YYYY",
        invoiceLimit: "10",
        emailNotifications: true,
        approvalNotifications: true,
        autoValidation: true,
      };
});

  const [saved, setSaved] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setSettings((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));

    setSaved(false);
  };

  const handleSave = () => {
    localStorage.setItem("ap_app_settings", JSON.stringify(settings));
    setSaved(true);
  };

  return (
    <div className="container-fluid py-3">
      <div className="page-heading mb-4">
        <div>
          <p className="eyebrow">WORKSPACE</p>
          <h1>Settings</h1>
          <p className="muted">
            Manage application preferences and configuration.
          </p>
        </div>
      </div>

      <div className="card p-4 mb-4">
        <h5 className="mb-3">Company Information</h5>

        <div className="mb-3">
          <label className="form-label">Company Name</label>
          <input
            className="form-control"
            name="companyName"
            value={settings.companyName}
            onChange={handleChange}
          />
        </div>

        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">Currency</label>
            <select
              className="form-select"
              name="currency"
              value={settings.currency}
              onChange={handleChange}
            >
              <option value="INR">INR - Indian Rupee</option>
              <option value="USD">USD - US Dollar</option>
              <option value="EUR">EUR - Euro</option>
            </select>
          </div>

          <div className="col-md-6 mb-3">
            <label className="form-label">Date Format</label>
            <select
              className="form-select"
              name="dateFormat"
              value={settings.dateFormat}
              onChange={handleChange}
            >
              <option value="DD-MM-YYYY">DD-MM-YYYY</option>
              <option value="MM-DD-YYYY">MM-DD-YYYY</option>
              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            </select>
          </div>
        </div>
      </div>

      <div className="card p-4 mb-4">
        <h5 className="mb-3">Invoice Configuration</h5>

        <div className="mb-3">
          <label className="form-label">Maximum Upload Size (MB)</label>
          <select
            className="form-select"
            name="invoiceLimit"
            value={settings.invoiceLimit}
            onChange={handleChange}
          >
            <option value="5">5 MB</option>
            <option value="10">10 MB</option>
            <option value="15">15 MB</option>
            <option value="20">20 MB</option>
          </select>
          <small className="text-muted">
            Note: This is a preference display only; it does not change the
            backend upload limit.
          </small>
        </div>

        <div className="form-check form-switch mb-3">
          <input
            className="form-check-input"
            type="checkbox"
            name="autoValidation"
            checked={settings.autoValidation}
            onChange={handleChange}
          />
          <label className="form-check-label">Enable automatic invoice validation</label>
        </div>
      </div>

      <div className="card p-4 mb-4">
        <h5 className="mb-3">Notifications</h5>

        <div className="form-check form-switch mb-3">
          <input
            className="form-check-input"
            type="checkbox"
            name="emailNotifications"
            checked={settings.emailNotifications}
            onChange={handleChange}
          />
          <label className="form-check-label">Email notifications</label>
        </div>

        <div className="form-check form-switch">
          <input
            className="form-check-input"
            type="checkbox"
            name="approvalNotifications"
            checked={settings.approvalNotifications}
            onChange={handleChange}
          />
          <label className="form-check-label">Invoice approval notifications</label>
        </div>
      </div>

      <div className="d-flex align-items-center gap-3">
        <button className="btn btn-primary" onClick={handleSave}>
          Save Settings
        </button>

        {saved && (
          <span className="text-success">
            Settings saved successfully.
          </span>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState(
    () => localStorage.getItem('access_token')
  )

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setToken(null)
  }

  if (!token) {
    return <Login onLogin={setToken} />
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">AP</div>
          <div>
            <strong>AP Flow</strong>
            <small>Finance Operations</small>
          </div>
        </div>

        <div className="nav-caption">WORKSPACE</div>
        <nav>
          {navItems.map(([path, label]) => (
            <NavLink key={path} to={path} end={path === '/'}>
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span className="status-dot" /> Development environment
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <span>Accounts Payable Automation</span>
          <button className="logout-button" onClick={logout}>Logout</button>
        </header>

        <div className="content-wrap">
          <Routes>
  <Route path="/" element={<Dashboard />} />
  <Route path="/invoices" element={<Invoices />} />
  <Route path="/upload" element={<InvoiceUpload />} />
  <Route path="/approvals" element={<Approvals />} />

  <Route path="/settings" element={<Settings />} />
<Route path="/vendors" element={<Vendors />} />
<Route path="/purchase-orders" element={<PurchaseOrders />} />
<Route path="/grn" element={<GoodsReceipts />} />
<Route path="/payments" element={<Payments />} />
<Route path="/reports" element={<Reports />} />
<Route path="/audit-logs" element={<AuditLogs />} />
<Route path="/settings" element={<div className="page-heading"><div><p className="eyebrow">WORKSPACE</p><h1>Settings</h1><p className="muted">Application settings.</p></div></div>} />

</Routes>
        </div>
      </main>
    </div>
  )
}
