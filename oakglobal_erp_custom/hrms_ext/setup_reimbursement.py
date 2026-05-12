import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import field


REIMBURSEMENT_PERMS = [
    {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "HR Manager", "read": 1, "write": 1, "create": 1},
    {"role": "Payroll Manager", "read": 1, "write": 1, "create": 1},
    {"role": "Department Manager", "read": 1},
    {"role": "Employee Self Service", "read": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
]

LOG_PERMS = [
    {"role": "HR Admin", "read": 1},
    {"role": "HR Manager", "read": 1},
    {"role": "Payroll Manager", "read": 1, "write": 1, "create": 1},
    {"role": "Payroll User", "read": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
]


def ensure_custom_doctype(name, fields, perms, title_field=None):
    if frappe.db.exists("DocType", name):
        return
    d = frappe.new_doc("DocType")
    d.name = name
    d.module = "Oakglobal ERP Custom"
    d.custom = 1
    d.track_changes = 1
    d.allow_rename = 0
    if title_field:
        d.title_field = title_field
    for f in fields:
        d.append("fields", f)
    for p in perms:
        d.append("permissions", p)
    d.insert(ignore_permissions=True)


def ensure_reimbursement_doctypes():
    ensure_custom_doctype("Reimbursement Policy", [
        field("policy_name", "Policy Name", "Data", reqd=1, in_list_view=1),
        field("company", "Company", "Link", options="Company", in_list_view=1),
        field("expense_claim_type", "Expense Claim Type", "Link", options="Expense Claim Type", in_list_view=1),
        field("period_type", "Period Type", "Select", options="Monthly\nQuarterly\nAnnual\nPer Claim", default="Monthly"),
        field("limit_amount", "Limit Amount", "Currency", reqd=1, in_list_view=1),
        field("requires_receipt", "Requires Receipt", "Check", default=1),
        field("over_limit_requires_hr", "Over Limit Requires HR Approval", "Check", default=1),
        field("pay_through_payroll", "Pay Through Payroll", "Check"),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("notes", "Notes", "Small Text"),
    ], REIMBURSEMENT_PERMS, "policy_name")

    ensure_custom_doctype("Reimbursement Balance", [
        field("employee", "Employee", "Link", options="Employee", reqd=1, in_list_view=1),
        field("policy", "Policy", "Link", options="Reimbursement Policy", reqd=1, in_list_view=1),
        field("period_start", "Period Start", "Date", reqd=1, in_list_view=1),
        field("period_end", "Period End", "Date", reqd=1, in_list_view=1),
        field("opening_balance", "Opening Balance", "Currency"),
        field("used_amount", "Used Amount", "Currency", read_only=1),
        field("reserved_amount", "Reserved Amount", "Currency", read_only=1),
        field("available_balance", "Available Balance", "Currency", read_only=1, in_list_view=1),
        field("status", "Status", "Select", options="Open\nClosed\nFrozen", default="Open", in_list_view=1),
        field("notes", "Notes", "Small Text"),
    ], REIMBURSEMENT_PERMS)

    ensure_custom_doctype("Reimbursement Disbursement Log", [
        field("expense_claim", "Expense Claim", "Link", options="Expense Claim", reqd=1, in_list_view=1),
        field("employee", "Employee", "Link", options="Employee", in_list_view=1),
        field("payroll_disbursement_batch", "Payroll Disbursement Batch", "Link", options="Payroll Disbursement Batch"),
        field("amount", "Amount", "Currency", reqd=1, in_list_view=1),
        field("payment_method", "Payment Method", "Select", options="Payroll\nBank Transfer\nCash\nOther", default="Payroll"),
        field("status", "Status", "Select", options="Pending\nQueued\nPaid\nFailed\nCancelled", default="Pending", in_list_view=1),
        field("processed_on", "Processed On", "Datetime"),
        field("message", "Message", "Small Text"),
    ], LOG_PERMS)


def ensure_expense_claim_fields():
    if not frappe.db.exists("DocType", "Expense Claim"):
        return
    create_custom_fields({
        "Expense Claim": [
            field("reimbursement_section", "Reimbursement Controls", "Section Break", insert_after="remark"),
            field("reimbursement_policy", "Reimbursement Policy", "Link", options="Reimbursement Policy", insert_after="reimbursement_section"),
            field("reimbursement_balance", "Reimbursement Balance", "Link", options="Reimbursement Balance", insert_after="reimbursement_policy"),
            field("reimbursement_preflight_status", "Reimbursement Preflight Status", "Select", options="Not Checked\nPassed\nWarning\nBlocked", default="Not Checked", insert_after="reimbursement_balance"),
            field("reimbursement_preflight_note", "Reimbursement Preflight Note", "Small Text", read_only=1, insert_after="reimbursement_preflight_status"),
            field("pay_through_payroll", "Pay Through Payroll", "Check", insert_after="reimbursement_preflight_note"),
            field("reimbursement_disbursement_log", "Reimbursement Disbursement Log", "Link", options="Reimbursement Disbursement Log", read_only=1, insert_after="pay_through_payroll"),
        ],
    }, update=True)


def run():
    ensure_reimbursement_doctypes()
    ensure_expense_claim_fields()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    run()
    for dt in ["Reimbursement Policy", "Reimbursement Balance", "Reimbursement Disbursement Log"]:
        if not frappe.db.exists("DocType", dt):
            raise Exception(f"missing doctype {dt}")
    if frappe.db.exists("DocType", "Expense Claim"):
        for fn in ["reimbursement_policy", "reimbursement_preflight_status", "pay_through_payroll"]:
            if not frappe.db.exists("Custom Field", {"dt": "Expense Claim", "fieldname": fn}):
                raise Exception(f"missing Expense Claim.{fn}")
    frappe.db.rollback()
    return "REIMBURSEMENT_SETUP_SMOKE_OK"
