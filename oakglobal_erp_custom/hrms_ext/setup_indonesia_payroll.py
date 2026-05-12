import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import field


PAYROLL_PERMS = [
    {"role": "Payroll Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Payroll User", "read": 1, "write": 1, "create": 1},
    {"role": "HR Admin", "read": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
]

READ_PERMS = [
    {"role": "Payroll Manager", "read": 1},
    {"role": "Payroll User", "read": 1},
    {"role": "HR Admin", "read": 1},
    {"role": "System Manager", "read": 1},
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


def ensure_indonesia_payroll_doctypes():
    ensure_custom_doctype("Indonesia Payroll Setting", [
        field("setting_name", "Setting Name", "Data", reqd=1, in_list_view=1),
        field("company", "Company", "Link", options="Company", in_list_view=1),
        field("effective_from", "Effective From", "Date", reqd=1, in_list_view=1),
        field("effective_to", "Effective To", "Date"),
        field("tax_method", "Tax Method", "Select", options="Gross\nGross Up\nNet", default="Gross", in_list_view=1),
        field("bpjs_enabled", "BPJS Enabled", "Check", default=1),
        field("thr_enabled", "THR Enabled", "Check", default=1),
        field("overtime_enabled", "Overtime Enabled", "Check", default=1),
        field("status", "Status", "Select", options="Draft\nActive\nInactive", default="Draft", in_list_view=1),
        field("notes", "Notes", "Small Text"),
    ], PAYROLL_PERMS, "setting_name")

    ensure_custom_doctype("BPJS Profile", [
        field("profile_name", "Profile Name", "Data", reqd=1, in_list_view=1),
        field("effective_from", "Effective From", "Date", reqd=1, in_list_view=1),
        field("health_employee_rate", "Health Employee Rate (%)", "Percent"),
        field("health_employer_rate", "Health Employer Rate (%)", "Percent"),
        field("jht_employee_rate", "JHT Employee Rate (%)", "Percent"),
        field("jht_employer_rate", "JHT Employer Rate (%)", "Percent"),
        field("jp_employee_rate", "JP Employee Rate (%)", "Percent"),
        field("jp_employer_rate", "JP Employer Rate (%)", "Percent"),
        field("jkk_employer_rate", "JKK Employer Rate (%)", "Percent"),
        field("jkm_employer_rate", "JKM Employer Rate (%)", "Percent"),
        field("wage_cap", "Wage Cap", "Currency"),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("notes", "Notes", "Small Text"),
    ], PAYROLL_PERMS, "profile_name")

    ensure_custom_doctype("PPh21 Profile", [
        field("profile_name", "Profile Name", "Data", reqd=1, in_list_view=1),
        field("effective_from", "Effective From", "Date", reqd=1, in_list_view=1),
        field("calculation_method", "Calculation Method", "Select", options="TER\nProgressive Annualized\nManual", default="TER", in_list_view=1),
        field("tax_category", "Tax Category", "Select", options="A\nB\nC\nManual", default="A"),
        field("ptkp_status", "Default PTKP Status", "Select", options="TK/0\nTK/1\nTK/2\nTK/3\nK/0\nK/1\nK/2\nK/3", default="TK/0"),
        field("non_npwp_multiplier", "Non NPWP Multiplier", "Float", default=1.2),
        field("gross_up_enabled", "Gross Up Enabled", "Check"),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("notes", "Notes", "Small Text"),
    ], PAYROLL_PERMS, "profile_name")

    ensure_custom_doctype("THR Rule", [
        field("rule_name", "Rule Name", "Data", reqd=1, in_list_view=1),
        field("company", "Company", "Link", options="Company", in_list_view=1),
        field("effective_from", "Effective From", "Date", reqd=1, in_list_view=1),
        field("minimum_service_months", "Minimum Service Months", "Int", default=1),
        field("full_thr_after_months", "Full THR After Months", "Int", default=12),
        field("base_component", "Base Component", "Link", options="Salary Component"),
        field("prorate_method", "Prorate Method", "Select", options="Monthly Service / 12\nManual\nNone", default="Monthly Service / 12"),
        field("payment_month", "Payment Month", "Select", options="Ramadan/Eid\nDecember\nManual", default="Ramadan/Eid"),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("notes", "Notes", "Small Text"),
    ], PAYROLL_PERMS, "rule_name")

    ensure_custom_doctype("Payroll Preflight Issue", [
        field("payroll_entry", "Payroll Entry", "Link", options="Payroll Entry", in_list_view=1),
        field("salary_slip", "Salary Slip", "Link", options="Salary Slip"),
        field("employee", "Employee", "Link", options="Employee", in_list_view=1),
        field("issue_type", "Issue Type", "Select", options="Missing BPJS Number\nMissing Tax Status\nMissing Salary Structure\nMissing Attendance Trace\nMissing Payroll Setting\nInvalid THR Rule\nOther", reqd=1, in_list_view=1),
        field("severity", "Severity", "Select", options="Info\nWarning\nBlocker", default="Warning", in_list_view=1),
        field("status", "Status", "Select", options="Open\nResolved\nIgnored", default="Open", in_list_view=1),
        field("message", "Message", "Small Text", reqd=1),
        field("detected_on", "Detected On", "Datetime", default="Now", in_list_view=1),
        field("resolved_on", "Resolved On", "Datetime"),
    ], READ_PERMS)


def ensure_payroll_custom_fields():
    create_custom_fields({
        "Salary Slip": [
            field("indonesia_payroll_section", "Indonesia Payroll", "Section Break", insert_after="payroll_trace_note"),
            field("indonesia_payroll_setting", "Indonesia Payroll Setting", "Link", options="Indonesia Payroll Setting", insert_after="indonesia_payroll_section"),
            field("bpjs_profile", "BPJS Profile", "Link", options="BPJS Profile", insert_after="indonesia_payroll_setting"),
            field("pph21_profile", "PPh21 Profile", "Link", options="PPh21 Profile", insert_after="bpjs_profile"),
            field("thr_rule", "THR Rule", "Link", options="THR Rule", insert_after="pph21_profile"),
            field("payroll_preflight_status", "Payroll Preflight Status", "Select", options="Not Checked\nPassed\nWarning\nBlocked", default="Not Checked", insert_after="thr_rule"),
            field("payroll_preflight_note", "Payroll Preflight Note", "Small Text", read_only=1, insert_after="payroll_preflight_status"),
        ],
    }, update=True)


def run():
    ensure_indonesia_payroll_doctypes()
    ensure_payroll_custom_fields()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    run()
    for dt in ["Indonesia Payroll Setting", "BPJS Profile", "PPh21 Profile", "THR Rule", "Payroll Preflight Issue"]:
        if not frappe.db.exists("DocType", dt):
            raise Exception(f"missing doctype {dt}")
    for fn in ["indonesia_payroll_setting", "bpjs_profile", "pph21_profile", "thr_rule", "payroll_preflight_status"]:
        if not frappe.db.exists("Custom Field", {"dt": "Salary Slip", "fieldname": fn}):
            raise Exception(f"missing Salary Slip.{fn}")
    frappe.db.rollback()
    return "INDONESIA_PAYROLL_SETUP_SMOKE_OK"
