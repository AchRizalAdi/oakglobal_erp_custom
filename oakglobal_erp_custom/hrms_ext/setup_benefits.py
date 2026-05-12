import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import field


BENEFIT_PERMS = [
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
    {"role": "Payroll Manager", "read": 1},
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


def ensure_benefit_doctypes():
    ensure_custom_doctype("Benefit Policy", [
        field("policy_name", "Policy Name", "Data", reqd=1, in_list_view=1),
        field("company", "Company", "Link", options="Company", in_list_view=1),
        field("benefit_type", "Benefit Type", "Select", options="Health\nAllowance\nInsurance\nLoan\nAdvance\nOther", reqd=1, in_list_view=1),
        field("effective_from", "Effective From", "Date", reqd=1, in_list_view=1),
        field("effective_to", "Effective To", "Date"),
        field("annual_limit", "Annual Limit", "Currency"),
        field("requires_approval", "Requires Approval", "Check", default=1),
        field("taxable", "Taxable", "Check"),
        field("payroll_component", "Payroll Component", "Link", options="Salary Component"),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("notes", "Notes", "Small Text"),
    ], BENEFIT_PERMS, "policy_name")

    ensure_custom_doctype("Benefit Utilization Log", [
        field("employee", "Employee", "Link", options="Employee", reqd=1, in_list_view=1),
        field("benefit_policy", "Benefit Policy", "Link", options="Benefit Policy", in_list_view=1),
        field("source_doctype", "Source DocType", "Link", options="DocType", reqd=1),
        field("source_name", "Source Name", "Dynamic Link", options="source_doctype", reqd=1, in_list_view=1),
        field("posting_date", "Posting Date", "Date", reqd=1, in_list_view=1),
        field("amount", "Amount", "Currency", reqd=1, in_list_view=1),
        field("status", "Status", "Select", options="Reserved\nApproved\nPaid\nCancelled", default="Reserved", in_list_view=1),
        field("payroll_source_trace", "Payroll Source Trace", "Link", options="Payroll Source Trace"),
        field("notes", "Notes", "Small Text"),
    ], LOG_PERMS)


def ensure_benefit_custom_fields():
    fields = {}
    if frappe.db.exists("DocType", "Employee Benefit Application"):
        fields["Employee Benefit Application"] = [
            field("benefit_controls_section", "Benefit Controls", "Section Break", insert_after="amended_from"),
            field("benefit_policy", "Benefit Policy", "Link", options="Benefit Policy", insert_after="benefit_controls_section"),
            field("benefit_preflight_status", "Benefit Preflight Status", "Select", options="Not Checked\nPassed\nWarning\nBlocked", default="Not Checked", insert_after="benefit_policy"),
            field("benefit_preflight_note", "Benefit Preflight Note", "Small Text", read_only=1, insert_after="benefit_preflight_status"),
        ]
    if frappe.db.exists("DocType", "Employee Benefit Claim"):
        fields["Employee Benefit Claim"] = [
            field("benefit_controls_section", "Benefit Controls", "Section Break", insert_after="amended_from"),
            field("benefit_policy", "Benefit Policy", "Link", options="Benefit Policy", insert_after="benefit_controls_section"),
            field("benefit_utilization_log", "Benefit Utilization Log", "Link", options="Benefit Utilization Log", read_only=1, insert_after="benefit_policy"),
            field("payroll_source_trace", "Payroll Source Trace", "Link", options="Payroll Source Trace", read_only=1, insert_after="benefit_utilization_log"),
        ]
    if fields:
        create_custom_fields(fields, update=True)


def run():
    ensure_benefit_doctypes()
    ensure_benefit_custom_fields()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    run()
    for dt in ["Benefit Policy", "Benefit Utilization Log"]:
        if not frappe.db.exists("DocType", dt):
            raise Exception(f"missing doctype {dt}")
    if frappe.db.exists("DocType", "Employee Benefit Application"):
        if not frappe.db.exists("Custom Field", {"dt": "Employee Benefit Application", "fieldname": "benefit_policy"}):
            raise Exception("missing Employee Benefit Application.benefit_policy")
    if frappe.db.exists("DocType", "Employee Benefit Claim"):
        if not frappe.db.exists("Custom Field", {"dt": "Employee Benefit Claim", "fieldname": "benefit_policy"}):
            raise Exception("missing Employee Benefit Claim.benefit_policy")
    frappe.db.rollback()
    return "BENEFITS_SETUP_SMOKE_OK"
