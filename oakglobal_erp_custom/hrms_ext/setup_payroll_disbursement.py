import frappe

from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import field


PAYROLL_PERMS = [
    {"role": "Payroll Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
    {"role": "Payroll User", "read": 1, "write": 1, "create": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
]

READ_PERMS = [
    {"role": "Payroll Manager", "read": 1},
    {"role": "Payroll User", "read": 1},
    {"role": "System Manager", "read": 1},
]


def ensure_custom_doctype(name, fields, perms=None, title_field=None, is_child=0, submit=0):
    if frappe.db.exists("DocType", name):
        return
    d = frappe.new_doc("DocType")
    d.name = name
    d.module = "Oakglobal ERP Custom"
    d.custom = 1
    d.track_changes = 1
    d.allow_rename = 0
    d.istable = is_child
    d.is_submittable = submit
    if title_field:
        d.title_field = title_field
    for f in fields:
        d.append("fields", f)
    if not is_child:
        for p in perms or []:
            d.append("permissions", p)
    d.insert(ignore_permissions=True)


def ensure_disbursement_doctypes():
    ensure_custom_doctype("Payroll Disbursement Line", [
        field("employee", "Employee", "Link", options="Employee", reqd=1, in_list_view=1),
        field("salary_slip", "Salary Slip", "Link", options="Salary Slip", in_list_view=1),
        field("bank_account_name", "Bank Account Name", "Data"),
        field("bank_account_no_masked", "Bank Account No Masked", "Data"),
        field("amount", "Amount", "Currency", reqd=1, in_list_view=1),
        field("preflight_status", "Preflight Status", "Data", in_list_view=1),
        field("payment_status", "Payment Status", "Select", options="Pending\nExported\nPaid\nFailed\nHeld", default="Pending", in_list_view=1),
        field("remarks", "Remarks", "Small Text"),
    ], is_child=1)

    ensure_custom_doctype("Payroll Disbursement Batch", [
        field("batch_name", "Batch Name", "Data", reqd=1, in_list_view=1),
        field("company", "Company", "Link", options="Company", reqd=1, in_list_view=1),
        field("payroll_entry", "Payroll Entry", "Link", options="Payroll Entry", in_list_view=1),
        field("posting_date", "Posting Date", "Date", reqd=1, in_list_view=1),
        field("bank_account", "Company Bank Account", "Link", options="Bank Account"),
        field("status", "Status", "Select", options="Draft\nReady\nExported\nPaid\nCancelled", default="Draft", in_list_view=1),
        field("total_amount", "Total Amount", "Currency", read_only=1, in_list_view=1),
        field("line_count", "Line Count", "Int", read_only=1),
        field("lines_section", "Lines", "Section Break"),
        field("lines", "Lines", "Table", options="Payroll Disbursement Line"),
        field("notes", "Notes", "Small Text"),
    ], PAYROLL_PERMS, "batch_name", submit=1)

    ensure_custom_doctype("Payroll Bank Export Log", [
        field("batch", "Payroll Disbursement Batch", "Link", options="Payroll Disbursement Batch", reqd=1, in_list_view=1),
        field("export_format", "Export Format", "Select", options="CSV\nBank Portal\nManual\nOther", default="CSV", in_list_view=1),
        field("exported_by", "Exported By", "Link", options="User", in_list_view=1),
        field("exported_on", "Exported On", "Datetime", default="Now", in_list_view=1),
        field("file_attachment", "File Attachment", "Attach"),
        field("status", "Status", "Select", options="Generated\nDownloaded\nUploaded\nFailed", default="Generated", in_list_view=1),
        field("message", "Message", "Small Text"),
    ], READ_PERMS)


def run():
    ensure_disbursement_doctypes()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    run()
    for dt in ["Payroll Disbursement Line", "Payroll Disbursement Batch", "Payroll Bank Export Log"]:
        if not frappe.db.exists("DocType", dt):
            raise Exception(f"missing doctype {dt}")
    frappe.db.rollback()
    return "PAYROLL_DISBURSEMENT_SETUP_SMOKE_OK"
