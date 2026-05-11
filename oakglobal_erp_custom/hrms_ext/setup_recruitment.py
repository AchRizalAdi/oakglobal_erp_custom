import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import field


RECRUITMENT_PERMS = [
    {"role": "Recruiter", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
    {"role": "HR Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
    {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
    {"role": "Department Manager", "read": 1, "write": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
]

CONFIG_PERMS = [
    {"role": "Recruiter", "read": 1},
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


def ensure_recruitment_doctypes():
    ensure_custom_doctype("Recruitment Pipeline Rule", [
        field("rule_name", "Rule Name", "Data", reqd=1, in_list_view=1),
        field("department", "Department", "Link", options="Department", in_list_view=1),
        field("designation", "Designation", "Link", options="Designation"),
        field("opening_type", "Opening Type", "Select", options="New Position\nReplacement\nContract\nInternship", default="New Position"),
        field("requires_manpower_reference", "Requires Manpower Reference", "Check", default=1),
        field("requires_assessment", "Requires Assessment", "Check", default=1),
        field("minimum_score", "Minimum Score", "Float", default=70),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
    ], CONFIG_PERMS)

    ensure_custom_doctype("Applicant Assessment", [
        field("job_applicant", "Job Applicant", "Link", options="Job Applicant", reqd=1, in_list_view=1),
        field("job_opening", "Job Opening", "Link", options="Job Opening", in_list_view=1),
        field("assessment_type", "Assessment Type", "Select", options="Screening\nTechnical\nPsychological\nBackground Check\nMedical\nOther", reqd=1, in_list_view=1),
        field("assessment_date", "Assessment Date", "Date", reqd=1, in_list_view=1),
        field("assessor", "Assessor", "Link", options="User"),
        field("score", "Score", "Float", in_list_view=1),
        field("result", "Result", "Select", options="Pending\nPassed\nFailed\nNeeds Review", default="Pending", in_list_view=1),
        field("attachment", "Attachment", "Attach"),
        field("notes", "Notes", "Small Text"),
    ], RECRUITMENT_PERMS, submit=1)

    ensure_custom_doctype("Candidate Scorecard", [
        field("job_applicant", "Job Applicant", "Link", options="Job Applicant", reqd=1, in_list_view=1),
        field("job_opening", "Job Opening", "Link", options="Job Opening", in_list_view=1),
        field("interview", "Interview", "Link", options="Interview"),
        field("reviewer", "Reviewer", "Link", options="User", reqd=1),
        field("technical_score", "Technical Score", "Float"),
        field("culture_score", "Culture Score", "Float"),
        field("experience_score", "Experience Score", "Float"),
        field("communication_score", "Communication Score", "Float"),
        field("final_score", "Final Score", "Float", read_only=1, in_list_view=1),
        field("recommendation", "Recommendation", "Select", options="Hire\nHold\nReject\nNeeds More Interview", reqd=1, in_list_view=1),
        field("review_notes", "Review Notes", "Small Text"),
    ], RECRUITMENT_PERMS, submit=1)


def ensure_recruitment_fields():
    create_custom_fields({
        "Job Opening": [
            field("recruitment_control_section", "Recruitment Control", "Section Break"),
            field("staffing_plan_reference", "Staffing Plan Reference", "Link", options="Staffing Plan"),
            field("job_requisition_reference", "Job Requisition Reference", "Link", options="Job Requisition"),
            field("recruitment_pipeline_rule", "Recruitment Pipeline Rule", "Link", options="Recruitment Pipeline Rule"),
            field("target_hiring_date", "Target Hiring Date", "Date"),
        ],
        "Job Applicant": [
            field("recruitment_screening_section", "Recruitment Screening", "Section Break"),
            field("screening_status", "Screening Status", "Select", options="New\nScreening\nShortlisted\nAssessment\nInterview\nOffered\nRejected\nHired", default="New", in_list_view=1),
            field("assessment_summary", "Assessment Summary", "Small Text"),
            field("scorecard_average", "Scorecard Average", "Float", read_only=1),
            field("onboarding_handoff_status", "Onboarding Handoff Status", "Select", options="Not Started\nReady\nStarted\nCompleted\nBlocked", default="Not Started", in_list_view=1),
        ],
        "Job Offer": [
            field("onboarding_handoff_section", "Onboarding Handoff", "Section Break"),
            field("employee_onboarding", "Employee Onboarding", "Link", options="Employee Onboarding", read_only=1),
            field("handoff_note", "Handoff Note", "Small Text"),
        ],
    }, update=True)


def run():
    ensure_recruitment_doctypes()
    ensure_recruitment_fields()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    run()
    for dt in ["Recruitment Pipeline Rule", "Applicant Assessment", "Candidate Scorecard"]:
        if not frappe.db.exists("DocType", dt):
            raise Exception(f"missing doctype {dt}")
    for dt, fn in [("Job Opening", "staffing_plan_reference"), ("Job Applicant", "screening_status"), ("Job Offer", "employee_onboarding")]:
        if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fn}):
            raise Exception(f"missing {dt}.{fn}")
    frappe.db.rollback()
    return "RECRUITMENT_SETUP_SMOKE_OK"
