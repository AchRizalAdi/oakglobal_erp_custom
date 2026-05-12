app_name = "oakglobal_erp_custom"
app_title = "Oakglobal ERP Custom"
app_publisher = "Oakglobal Maritim"
app_description = "Custom ERPNext app for Oakglobal Maritim"
app_email = "admin@oakglobalmaritim.com"
app_license = "MIT"

# Website assets. Keep ERPNext core untouched.
# web_include_css = [
#     "/assets/oakglobal_erp_custom/css/oakglobal_login.css",
# ]

# Version-controlled HRMS customizations. Keep filters tight to avoid exporting unrelated setup.
fixtures = [
    {"doctype": "Role", "filters": [["role_name", "in", ["HR Admin", "HR Manager", "Payroll Manager", "Payroll User", "Department Manager", "Employee Self Service", "Recruiter", "Performance Reviewer"]]]},
    {"doctype": "Custom Field", "filters": [["dt", "in", ["Employee", "HR Request", "Employee Data Change Request", "Employee Checkin", "Attendance Request", "Salary Slip", "Overtime Slip", "Job Opening", "Job Applicant", "Job Offer"]]]},
    {"doctype": "DocType", "filters": [["name", "in", ["HR Request", "Employee Data Change Request", "Employee Data Change Request Field", "Attendance Location", "Attendance Geofence", "Attendance Validation Rule", "Attendance Validation Log", "Attendance Validation Exception", "Payroll Source Trace", "Shift Change Request", "Attendance Correction Request", "HR Document Request", "HR Letter Template", "Asset Assignment", "Helpdesk Ticket", "Announcement", "Recruitment Pipeline Rule", "Applicant Assessment", "Candidate Scorecard", "Webhook Endpoint", "Integration Log", "External Attendance Import", "Attendance Device", "Device Integration Setting", "Payroll Journal Mapping", "Indonesia Payroll Setting", "BPJS Profile", "PPh21 Profile", "THR Rule", "Payroll Preflight Issue"]]]},
    {"doctype": "Workflow", "filters": [["document_type", "in", ["HR Request", "Employee Data Change Request"]]]},
    "Workflow State",
    "Workflow Action Master",
    {"doctype": "Custom DocPerm", "filters": [["parent", "in", ["HR Request", "Employee Data Change Request", "Employee Data Change Request Field", "Attendance Location", "Attendance Geofence", "Attendance Validation Rule", "Attendance Validation Log", "Attendance Validation Exception", "Payroll Source Trace", "Shift Change Request", "Attendance Correction Request", "HR Document Request", "HR Letter Template", "Asset Assignment", "Helpdesk Ticket", "Announcement", "Recruitment Pipeline Rule", "Applicant Assessment", "Candidate Scorecard", "Webhook Endpoint", "Integration Log", "External Attendance Import", "Attendance Device", "Device Integration Setting", "Payroll Journal Mapping", "Indonesia Payroll Setting", "BPJS Profile", "PPh21 Profile", "THR Rule", "Payroll Preflight Issue"]]]},
    {"doctype": "Report", "filters": [["name", "in", ["Employee Request Center", "Manager Approval Dashboard", "Team Attendance Summary", "Team Leave Calendar", "Pending Approval Items"]]]},
    {"doctype": "Workspace", "filters": [["name", "in", ["Employee Self Service", "Manager Self Service"]]]},
]

doc_events = {
    "Employee Data Change Request": {
        "on_update": "oakglobal_erp_custom.hrms_ext.employee_data_change.apply_approved_changes",
    },
    "Employee Checkin": {
        "validate": "oakglobal_erp_custom.hrms_ext.attendance_geofence.validate_checkin",
        "after_insert": "oakglobal_erp_custom.hrms_ext.attendance_geofence.log_checkin_validation",
    },
}
