import frappe

from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import field


INTEGRATION_PERMS = [
    {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "HR Manager", "read": 1, "write": 1, "create": 1},
    {"role": "Payroll Manager", "read": 1, "write": 1, "create": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
]

LOG_PERMS = [
    {"role": "HR Admin", "read": 1, "write": 1, "create": 1},
    {"role": "HR Manager", "read": 1},
    {"role": "Payroll Manager", "read": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
]


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


def ensure_integration_doctypes():
    ensure_custom_doctype("Webhook Endpoint", [
        field("endpoint_name", "Endpoint Name", "Data", reqd=1, in_list_view=1),
        field("event_type", "Event Type", "Select", options="Employee\nAttendance\nPayroll\nRecruitment\nHR Request\nAsset\nOther", reqd=1, in_list_view=1),
        field("target_url", "Target URL", "Data", reqd=1),
        field("http_method", "HTTP Method", "Select", options="POST\nPUT", default="POST"),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("last_status", "Last Status", "Data", read_only=1, in_list_view=1),
        field("last_sent_on", "Last Sent On", "Datetime", read_only=1),
        field("notes", "Notes", "Small Text"),
    ], INTEGRATION_PERMS)

    ensure_custom_doctype("Integration Log", [
        field("integration_type", "Integration Type", "Select", options="Webhook\nAttendance Device\nPayroll Journal\nExternal Import\nAPI\nOther", reqd=1, in_list_view=1),
        field("reference_doctype", "Reference DocType", "Link", options="DocType"),
        field("reference_name", "Reference Name", "Dynamic Link", options="reference_doctype"),
        field("direction", "Direction", "Select", options="Inbound\nOutbound", reqd=1, in_list_view=1),
        field("status", "Status", "Select", options="Queued\nSuccess\nFailed\nRetrying\nIgnored", reqd=1, in_list_view=1),
        field("attempt_count", "Attempt Count", "Int", default=0),
        field("request_payload", "Request Payload", "Code"),
        field("response_payload", "Response Payload", "Code"),
        field("error_message", "Error Message", "Small Text"),
        field("processed_on", "Processed On", "Datetime", in_list_view=1),
    ], LOG_PERMS)

    ensure_custom_doctype("Attendance Device", [
        field("device_name", "Device Name", "Data", reqd=1, in_list_view=1),
        field("device_type", "Device Type", "Select", options="Fingerprint\nFace Recognition\nMobile App\nWeb\nAPI\nOther", reqd=1, in_list_view=1),
        field("location", "Location", "Link", options="Attendance Location"),
        field("device_identifier", "Device Identifier", "Data", in_list_view=1),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("last_sync_on", "Last Sync On", "Datetime", read_only=1),
        field("notes", "Notes", "Small Text"),
    ], INTEGRATION_PERMS)

    ensure_custom_doctype("External Attendance Import", [
        field("import_source", "Import Source", "Data", reqd=1, in_list_view=1),
        field("device", "Device", "Link", options="Attendance Device"),
        field("employee", "Employee", "Link", options="Employee", in_list_view=1),
        field("employee_identifier", "Employee Identifier", "Data"),
        field("log_time", "Log Time", "Datetime", reqd=1, in_list_view=1),
        field("log_type", "Log Type", "Select", options="IN\nOUT", in_list_view=1),
        field("raw_payload", "Raw Payload", "Code"),
        field("sync_status", "Sync Status", "Select", options="Pending\nSynced\nFailed\nIgnored", default="Pending", in_list_view=1),
        field("employee_checkin", "Employee Checkin", "Link", options="Employee Checkin", read_only=1),
        field("error_message", "Error Message", "Small Text", read_only=1),
    ], LOG_PERMS)

    ensure_custom_doctype("Device Integration Setting", [
        field("setting_name", "Setting Name", "Data", reqd=1, in_list_view=1),
        field("device_type", "Device Type", "Select", options="Fingerprint\nFace Recognition\nMobile App\nWeb\nAPI\nOther", reqd=1),
        field("base_url", "Base URL", "Data"),
        field("auth_type", "Auth Type", "Select", options="None\nAPI Key\nBearer Token\nBasic\nCustom", default="None"),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("sync_interval_minutes", "Sync Interval Minutes", "Int", default=60),
        field("last_sync_on", "Last Sync On", "Datetime", read_only=1),
        field("notes", "Notes", "Small Text"),
    ], INTEGRATION_PERMS)

    ensure_custom_doctype("Payroll Journal Mapping", [
        field("mapping_name", "Mapping Name", "Data", reqd=1, in_list_view=1),
        field("company", "Company", "Link", options="Company", reqd=1, in_list_view=1),
        field("salary_component", "Salary Component", "Link", options="Salary Component", reqd=1, in_list_view=1),
        field("debit_account", "Debit Account", "Link", options="Account"),
        field("credit_account", "Credit Account", "Link", options="Account"),
        field("cost_center", "Cost Center", "Link", options="Cost Center"),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("notes", "Notes", "Small Text"),
    ], INTEGRATION_PERMS)


def run():
    ensure_integration_doctypes()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    run()
    for dt in [
        "Webhook Endpoint",
        "Integration Log",
        "External Attendance Import",
        "Attendance Device",
        "Device Integration Setting",
        "Payroll Journal Mapping",
    ]:
        if not frappe.db.exists("DocType", dt):
            raise Exception(f"missing doctype {dt}")
    frappe.db.rollback()
    return "ANALYTICS_INTEGRATION_SETUP_SMOKE_OK"
