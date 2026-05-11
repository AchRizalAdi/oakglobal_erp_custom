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
    {"doctype": "Custom Field", "filters": [["dt", "in", ["Employee", "HR Request", "Employee Data Change Request"]]]},
    {"doctype": "DocType", "filters": [["name", "in", ["HR Request", "Employee Data Change Request", "Employee Data Change Request Field"]]]},
    {"doctype": "Workflow", "filters": [["document_type", "in", ["HR Request", "Employee Data Change Request"]]]},
    "Workflow State",
    "Workflow Action Master",
    {"doctype": "Custom DocPerm", "filters": [["parent", "in", ["HR Request", "Employee Data Change Request", "Employee Data Change Request Field"]]]},
]

doc_events = {
    "Employee Data Change Request": {
        "on_update": "oakglobal_erp_custom.hrms_ext.employee_data_change.apply_approved_changes",
    }
}
