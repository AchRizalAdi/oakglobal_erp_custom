import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import field

TALENT_PERMS = [
    {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
    {"role": "HR Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
    {"role": "Performance Reviewer", "read": 1, "write": 1, "create": 1, "submit": 1},
    {"role": "Department Manager", "read": 1, "write": 1, "create": 1, "submit": 1},
    {"role": "Employee Self Service", "read": 1, "write": 1, "create": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
]

CONFIG_PERMS = [
    {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "HR Manager", "read": 1, "write": 1, "create": 1},
    {"role": "Performance Reviewer", "read": 1},
    {"role": "Department Manager", "read": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
]


def ensure_custom_doctype(name, fields, perms, submit=0, title_field=None):
    if frappe.db.exists("DocType", name):
        return
    d = frappe.new_doc("DocType")
    d.name = name
    d.module = "Oakglobal ERP Custom"
    d.custom = 1
    d.is_submittable = submit
    d.track_changes = 1
    d.allow_rename = 0
    if title_field:
        d.title_field = title_field
    for f in fields:
        d.append("fields", f)
    for p in perms:
        d.append("permissions", p)
    d.insert(ignore_permissions=True)


def ensure_talent_development_doctypes():
    ensure_custom_doctype("OKR Cycle", [
        field("cycle_name", "Cycle Name", "Data", reqd=1, in_list_view=1),
        field("company", "Company", "Link", options="Company", in_list_view=1),
        field("period_start", "Period Start", "Date", reqd=1, in_list_view=1),
        field("period_end", "Period End", "Date", reqd=1, in_list_view=1),
        field("review_frequency", "Review Frequency", "Select", options="Monthly\nQuarterly\nSemi Annual\nAnnual", default="Quarterly"),
        field("status", "Status", "Select", options="Draft\nActive\nClosed\nArchived", default="Draft", in_list_view=1),
        field("notes", "Notes", "Small Text"),
    ], CONFIG_PERMS, title_field="cycle_name")

    ensure_custom_doctype("Competency Map", [
        field("map_name", "Map Name", "Data", reqd=1, in_list_view=1),
        field("department", "Department", "Link", options="Department", in_list_view=1),
        field("designation", "Designation", "Link", options="Designation", in_list_view=1),
        field("skill", "Skill", "Link", options="Skill"),
        field("competency_area", "Competency Area", "Select", options="Technical\nLeadership\nCommunication\nCompliance\nSafety\nOther", reqd=1, in_list_view=1),
        field("required_level", "Required Level", "Select", options="Beginner\nWorking\nProficient\nAdvanced\nExpert", default="Working", in_list_view=1),
        field("is_mandatory", "Is Mandatory", "Check", default=1),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
    ], CONFIG_PERMS, title_field="map_name")

    ensure_custom_doctype("Individual Development Plan", [
        field("employee", "Employee", "Link", options="Employee", reqd=1, in_list_view=1),
        field("okr_cycle", "OKR Cycle", "Link", options="OKR Cycle", in_list_view=1),
        field("appraisal", "Appraisal", "Link", options="Appraisal"),
        field("goal", "Goal", "Link", options="Goal"),
        field("competency_map", "Competency Map", "Link", options="Competency Map"),
        field("development_area", "Development Area", "Data", reqd=1, in_list_view=1),
        field("action_plan", "Action Plan", "Small Text", reqd=1),
        field("target_date", "Target Date", "Date", reqd=1, in_list_view=1),
        field("training_program", "Training Program", "Link", options="Training Program"),
        field("mentor", "Mentor", "Link", options="Employee"),
        field("progress_percent", "Progress Percent", "Percent", in_list_view=1),
        field("status", "Status", "Select", options="Draft\nIn Progress\nCompleted\nDeferred\nCancelled", default="Draft", in_list_view=1),
        field("review_note", "Review Note", "Small Text"),
    ], TALENT_PERMS, submit=1)


def ensure_talent_development_fields():
    fields = {}
    if frappe.db.exists("DocType", "Appraisal"):
        fields["Appraisal"] = [
            field("talent_development_section", "Talent Development", "Section Break"),
            field("okr_cycle", "OKR Cycle", "Link", options="OKR Cycle", insert_after="talent_development_section"),
            field("development_plan", "Development Plan", "Link", options="Individual Development Plan", insert_after="okr_cycle"),
            field("competency_summary", "Competency Summary", "Small Text", insert_after="development_plan"),
        ]
    if frappe.db.exists("DocType", "Goal"):
        fields["Goal"] = [
            field("okr_tracking_section", "OKR Tracking", "Section Break"),
            field("okr_cycle", "OKR Cycle", "Link", options="OKR Cycle", insert_after="okr_tracking_section"),
            field("okr_weight", "OKR Weight", "Percent", insert_after="okr_cycle"),
            field("okr_progress_status", "OKR Progress Status", "Select", options="Not Started\nOn Track\nAt Risk\nCompleted\nDropped", default="Not Started", insert_after="okr_weight"),
        ]
    if frappe.db.exists("DocType", "Training Program"):
        fields["Training Program"] = [
            field("development_link_section", "Development Link", "Section Break"),
            field("competency_map", "Competency Map", "Link", options="Competency Map", insert_after="development_link_section"),
            field("target_role", "Target Role", "Link", options="Designation", insert_after="competency_map"),
        ]
    if fields:
        create_custom_fields(fields, update=True)


def run():
    ensure_talent_development_doctypes()
    ensure_talent_development_fields()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    run()
    for dt in ["OKR Cycle", "Competency Map", "Individual Development Plan"]:
        if not frappe.db.exists("DocType", dt):
            raise Exception(f"missing doctype {dt}")
    checks = [("Appraisal", "okr_cycle"), ("Goal", "okr_cycle"), ("Training Program", "competency_map")]
    for dt, fn in checks:
        if frappe.db.exists("DocType", dt) and not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fn}):
            raise Exception(f"missing {dt}.{fn}")
    frappe.db.rollback()
    return "TALENT_DEVELOPMENT_SETUP_SMOKE_OK"
