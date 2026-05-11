import frappe

from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import field


REQUEST_PERMS = [
    {"role": "Employee Self Service", "read": 1, "write": 1, "create": 1, "submit": 1},
    {"role": "Department Manager", "read": 1, "write": 1, "submit": 1},
    {"role": "HR Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
    {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
]

OPEN_PERMS = [
    {"role": "Employee Self Service", "read": 1, "write": 1, "create": 1},
    {"role": "Department Manager", "read": 1, "write": 1},
    {"role": "HR Manager", "read": 1, "write": 1, "create": 1},
    {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
]

CONFIG_PERMS = [
    {"role": "HR Manager", "read": 1, "write": 1, "create": 1},
    {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
]


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


def ensure_hr_document_request():
    ensure_custom_doctype("HR Document Request", [
        field("employee", "Employee", "Link", options="Employee", reqd=1, in_list_view=1),
        field("document_type", "Document Type", "Select", options="Employment Letter\nSalary Certificate\nReference Letter\nVisa Letter\nCustom", reqd=1, in_list_view=1),
        field("purpose", "Purpose", "Small Text", reqd=1),
        field("needed_by", "Needed By", "Date", in_list_view=1),
        field("letter_template", "Letter Template", "Link", options="HR Letter Template"),
        field("generated_file", "Generated File", "Attach", read_only=1),
        field("fulfillment_status", "Fulfillment Status", "Select", options="Pending\nIn Progress\nReady\nDelivered\nRejected", default="Pending", in_list_view=1),
        field("hr_note", "HR Note", "Small Text"),
    ], REQUEST_PERMS, submit=1)


def ensure_hr_letter_template():
    ensure_custom_doctype("HR Letter Template", [
        field("template_name", "Template Name", "Data", reqd=1, in_list_view=1),
        field("document_type", "Document Type", "Select", options="Employment Letter\nSalary Certificate\nReference Letter\nVisa Letter\nCustom", reqd=1, in_list_view=1),
        field("language", "Language", "Select", options="Indonesian\nEnglish", default="Indonesian"),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("template_body", "Template Body", "Text Editor", reqd=1),
    ], CONFIG_PERMS)


def ensure_asset_assignment():
    ensure_custom_doctype("Asset Assignment", [
        field("employee", "Employee", "Link", options="Employee", reqd=1, in_list_view=1),
        field("asset", "Asset", "Link", options="Asset", in_list_view=1),
        field("asset_name", "Asset Name", "Data", reqd=1, in_list_view=1),
        field("serial_no", "Serial No", "Data"),
        field("assigned_on", "Assigned On", "Date", reqd=1, in_list_view=1),
        field("expected_return_on", "Expected Return On", "Date"),
        field("returned_on", "Returned On", "Date"),
        field("condition_on_issue", "Condition On Issue", "Select", options="Good\nFair\nDamaged", default="Good"),
        field("condition_on_return", "Condition On Return", "Select", options="Good\nFair\nDamaged\nLost"),
        field("assignment_status", "Assignment Status", "Select", options="Assigned\nReturn Requested\nReturned\nLost\nWritten Off", default="Assigned", in_list_view=1),
        field("return_note", "Return Note", "Small Text"),
    ], REQUEST_PERMS, submit=1)


def ensure_helpdesk_ticket():
    ensure_custom_doctype("Helpdesk Ticket", [
        field("employee", "Employee", "Link", options="Employee", in_list_view=1),
        field("category", "Category", "Select", options="HR\nPayroll\nAttendance\nBenefit\nAsset\nIT\nOther", reqd=1, in_list_view=1),
        field("subject", "Subject", "Data", reqd=1, in_list_view=1),
        field("description", "Description", "Small Text", reqd=1),
        field("priority", "Priority", "Select", options="Low\nMedium\nHigh\nUrgent", default="Medium", in_list_view=1),
        field("ticket_status", "Ticket Status", "Select", options="Open\nIn Progress\nWaiting\nResolved\nClosed", default="Open", in_list_view=1),
        field("assigned_to", "Assigned To", "Link", options="User"),
        field("resolution", "Resolution", "Small Text"),
        field("resolved_on", "Resolved On", "Datetime", read_only=1),
    ], OPEN_PERMS)


def ensure_announcement():
    ensure_custom_doctype("Announcement", [
        field("title", "Title", "Data", reqd=1, in_list_view=1),
        field("audience", "Audience", "Select", options="All Employees\nDepartment\nBranch\nRole", default="All Employees", in_list_view=1),
        field("department", "Department", "Link", options="Department"),
        field("branch", "Branch", "Link", options="Branch"),
        field("role", "Role", "Link", options="Role"),
        field("publish_from", "Publish From", "Datetime", reqd=1, in_list_view=1),
        field("publish_until", "Publish Until", "Datetime"),
        field("content", "Content", "Text Editor", reqd=1),
        field("is_published", "Is Published", "Check", default=0, in_list_view=1),
    ], CONFIG_PERMS)


def run():
    ensure_hr_letter_template()
    ensure_hr_document_request()
    ensure_asset_assignment()
    ensure_helpdesk_ticket()
    ensure_announcement()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    run()
    for dt in ["HR Document Request", "HR Letter Template", "Asset Assignment", "Helpdesk Ticket", "Announcement"]:
        if not frappe.db.exists("DocType", dt):
            raise Exception(f"missing doctype {dt}")
    frappe.db.rollback()
    return "HR_ADMIN_SETUP_SMOKE_OK"
