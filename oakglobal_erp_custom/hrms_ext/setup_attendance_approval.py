import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import field


def ensure_custom_doctype(name, fields, perms, submit=0):
    if frappe.db.exists("DocType", name):
        return
    d = frappe.new_doc("DocType")
    d.name = name
    d.module = "Oakglobal ERP Custom"
    d.custom = 1
    d.is_submittable = submit
    d.track_changes = 1
    d.allow_rename = 0
    for f in fields:
        d.append("fields", f)
    for p in perms:
        d.append("permissions", p)
    d.insert(ignore_permissions=True)


def ensure_attendance_approval_doctypes():
    log_perms = [
        {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "HR Manager", "read": 1},
        {"role": "Department Manager", "read": 1},
        {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
    ]
    exception_perms = [
        {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
        {"role": "HR Manager", "read": 1, "write": 1, "create": 1, "submit": 1},
        {"role": "Department Manager", "read": 1, "write": 1, "create": 1, "submit": 1},
        {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
    ]
    ensure_custom_doctype("Attendance Validation Log", [
        field("employee_checkin", "Employee Checkin", "Link", options="Employee Checkin", reqd=1, in_list_view=1),
        field("employee", "Employee", "Link", options="Employee", in_list_view=1),
        field("attendance_location", "Attendance Location", "Link", options="Attendance Location", in_list_view=1),
        field("attendance_geofence", "Attendance Geofence", "Link", options="Attendance Geofence"),
        field("validation_status", "Validation Status", "Data", in_list_view=1),
        field("distance_from_geofence_meters", "Distance From Geofence Meters", "Float"),
        field("captured_latitude", "Captured Latitude", "Float"),
        field("captured_longitude", "Captured Longitude", "Float"),
        field("validation_message", "Validation Message", "Small Text"),
        field("logged_on", "Logged On", "Datetime", default="Now", read_only=1),
    ], log_perms)
    ensure_custom_doctype("Attendance Validation Exception", [
        field("employee_checkin", "Employee Checkin", "Link", options="Employee Checkin", reqd=1, in_list_view=1),
        field("employee", "Employee", "Link", options="Employee", in_list_view=1),
        field("attendance_request", "Attendance Request", "Link", options="Attendance Request"),
        field("exception_status", "Exception Status", "Select", options="Draft\nPending Approval\nApproved\nRejected", default="Draft", in_list_view=1),
        field("reason", "Reason", "Small Text", reqd=1),
        field("evidence", "Evidence", "Attach"),
        field("decision_section", "Decision", "Section Break"),
        field("approver", "Approver", "Link", options="User", read_only=1),
        field("decision_on", "Decision On", "Datetime", read_only=1),
        field("decision_note", "Decision Note", "Small Text"),
    ], exception_perms, submit=1)


def ensure_attendance_approval_fields():
    create_custom_fields({
        "Employee Checkin": [
            field("validation_exception", "Validation Exception", "Link", options="Attendance Validation Exception", insert_after="validation_message"),
            field("validation_override_status", "Validation Override Status", "Select", options="None\nPending Approval\nApproved\nRejected", default="None", read_only=1, insert_after="validation_exception"),
        ],
        "Attendance Request": [
            field("validation_exception", "Validation Exception", "Link", options="Attendance Validation Exception", insert_after="geofence_evidence"),
        ],
    }, update=True)


def run():
    ensure_attendance_approval_doctypes()
    ensure_attendance_approval_fields()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    run()
    for dt in ["Attendance Validation Log", "Attendance Validation Exception"]:
        if not frappe.db.exists("DocType", dt):
            raise Exception(f"missing doctype {dt}")
    for fn in ["validation_exception", "validation_override_status"]:
        if not frappe.db.exists("Custom Field", {"dt": "Employee Checkin", "fieldname": fn}):
            raise Exception(f"missing Employee Checkin.{fn}")
    frappe.db.rollback()
    return "ATTENDANCE_APPROVAL_SETUP_SMOKE_OK"
