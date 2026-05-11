import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import field


def ensure_custom_doctype(name, fields, perms):
    if frappe.db.exists("DocType", name):
        return
    d = frappe.new_doc("DocType")
    d.name = name
    d.module = "Oakglobal ERP Custom"
    d.custom = 1
    d.track_changes = 1
    d.allow_rename = 0
    for f in fields:
        d.append("fields", f)
    for p in perms:
        d.append("permissions", p)
    d.insert(ignore_permissions=True)


def ensure_payroll_trace_doctype():
    perms = [
        {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "HR Manager", "read": 1, "write": 1, "create": 1},
        {"role": "Payroll Manager", "read": 1, "write": 1, "create": 1},
        {"role": "Payroll User", "read": 1},
        {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
    ]
    ensure_custom_doctype("Payroll Source Trace", [
        field("employee", "Employee", "Link", options="Employee", reqd=1, in_list_view=1),
        field("company", "Company", "Link", options="Company", in_list_view=1),
        field("period_start", "Period Start", "Date", reqd=1, in_list_view=1),
        field("period_end", "Period End", "Date", reqd=1, in_list_view=1),
        field("source_type", "Source Type", "Select", options="Attendance\nEmployee Checkin\nLeave Application\nOvertime Slip\nExpense Claim\nAttendance Request\nAttendance Validation Exception\nManual", reqd=1, in_list_view=1),
        field("source_doctype", "Source DocType", "Link", options="DocType", reqd=1),
        field("source_name", "Source Name", "Dynamic Link", options="source_doctype", reqd=1, in_list_view=1),
        field("source_date", "Source Date", "Date", in_list_view=1),
        field("source_status", "Source Status", "Data", in_list_view=1),
        field("quantity", "Quantity", "Float"),
        field("amount", "Amount", "Currency"),
        field("salary_slip", "Salary Slip", "Link", options="Salary Slip"),
        field("payroll_entry", "Payroll Entry", "Link", options="Payroll Entry"),
        field("trace_note", "Trace Note", "Small Text"),
    ], perms)


def ensure_payroll_trace_fields():
    create_custom_fields({
        "Salary Slip": [
            field("payroll_trace_section", "Payroll Source Trace", "Section Break", insert_after="remarks"),
            field("payroll_trace_generated_on", "Payroll Trace Generated On", "Datetime", read_only=1, insert_after="payroll_trace_section"),
            field("attendance_source_count", "Attendance Source Count", "Int", read_only=1, insert_after="payroll_trace_generated_on"),
            field("exception_source_count", "Exception Source Count", "Int", read_only=1, insert_after="attendance_source_count"),
            field("payroll_trace_note", "Payroll Trace Note", "Small Text", read_only=1, insert_after="exception_source_count"),
        ],
    }, update=True)


def run():
    ensure_payroll_trace_doctype()
    ensure_payroll_trace_fields()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    run()
    if not frappe.db.exists("DocType", "Payroll Source Trace"):
        raise Exception("missing Payroll Source Trace")
    for fn in ["payroll_trace_generated_on", "attendance_source_count", "exception_source_count"]:
        if not frappe.db.exists("Custom Field", {"dt": "Salary Slip", "fieldname": fn}):
            raise Exception(f"missing Salary Slip.{fn}")
    frappe.db.rollback()
    return "PAYROLL_TRACE_SETUP_SMOKE_OK"
