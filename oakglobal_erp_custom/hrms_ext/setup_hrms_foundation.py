import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
ROLES=["HR Admin","HR Manager","Payroll Manager","Payroll User","Department Manager","Employee Self Service","Recruiter","Performance Reviewer"]
def field(fieldname,label,fieldtype,**kw):
    d={"fieldname":fieldname,"label":label,"fieldtype":fieldtype}; d.update(kw); return d
def ensure_roles():
    for role in ROLES:
        if not frappe.db.exists("Role", role):
            d=frappe.new_doc("Role"); d.role_name=role; d.desk_access=1; d.insert(ignore_permissions=True)
def ensure_employee_fields():
    create_custom_fields({"Employee":[
        field("hrms_foundation_section","HRMS Foundation","Section Break",insert_after="job_applicant"),
        field("branch_location","Branch Location","Data",insert_after="hrms_foundation_section"),
        field("work_location_type","Work Location Type","Select",options="Office\nRemote\nHybrid\nField\nBranch",insert_after="branch_location"),
        field("compliance_section","Compliance","Section Break",insert_after="work_location_type"),
        field("tax_status","Tax Status","Select",options="TK/0\nTK/1\nTK/2\nTK/3\nK/0\nK/1\nK/2\nK/3",insert_after="compliance_section"),
        field("bpjs_kesehatan_no","BPJS Kesehatan No","Data",insert_after="tax_status"),
        field("bpjs_ketenagakerjaan_no","BPJS Ketenagakerjaan No","Data",insert_after="bpjs_kesehatan_no"),
        field("bank_section","Bank Metadata","Section Break",insert_after="bpjs_ketenagakerjaan_no"),
        field("bank_account_name","Bank Account Name","Data",insert_after="bank_section"),
        field("bank_account_no_masked","Bank Account No Masked","Data",insert_after="bank_account_name"),
        field("emergency_section","Emergency Contact Detail","Section Break",insert_after="bank_account_no_masked"),
        field("emergency_contact_relation","Emergency Contact Relation","Data",insert_after="emergency_section"),
        field("hr_lifecycle_section","HR Lifecycle","Section Break",insert_after="emergency_contact_relation"),
        field("onboarding_status_detail","Onboarding Status Detail","Select",options="Not Started\nIn Progress\nCompleted\nBlocked",insert_after="hr_lifecycle_section"),
        field("offboarding_status_detail","Offboarding Status Detail","Select",options="Not Started\nIn Progress\nCompleted\nBlocked",insert_after="onboarding_status_detail"),
    ]}, update=True)
def ensure_doctype(name, fields, perms, istable=0, submit=0):
    if frappe.db.exists("DocType", name): return
    d=frappe.new_doc("DocType"); d.name=name; d.module="Oakglobal ERP Custom"; d.custom=1; d.istable=istable; d.is_submittable=submit; d.track_changes=1; d.allow_rename=0
    for f in fields: d.append("fields", f)
    for p in perms: d.append("permissions", p)
    d.insert(ignore_permissions=True)
def ensure_doctypes():
    ensure_doctype("Employee Data Change Request Field",[
        field("fieldname","Fieldname","Data",reqd=1,in_list_view=1), field("field_label","Field Label","Data",in_list_view=1), field("old_value","Old Value","Small Text",read_only=1), field("new_value","New Value","Small Text",reqd=1,in_list_view=1)], [], istable=1)
    perms=[{"role":"Employee Self Service","read":1,"write":1,"create":1,"submit":1},{"role":"Department Manager","read":1,"write":1,"submit":1},{"role":"HR Manager","read":1,"write":1,"create":1,"submit":1,"cancel":1,"amend":1},{"role":"HR Admin","read":1,"write":1,"create":1,"delete":1,"submit":1,"cancel":1,"amend":1},{"role":"System Manager","read":1,"write":1,"create":1,"delete":1,"submit":1,"cancel":1,"amend":1}]
    ensure_doctype("HR Request",[
        field("employee","Employee","Link",options="Employee",reqd=1,in_list_view=1), field("request_type","Request Type","Select",options="General\nDocument\nData Change\nAttendance\nPayroll\nBenefit\nAsset\nHelpdesk",reqd=1,in_list_view=1), field("subject","Subject","Data",reqd=1,in_list_view=1), field("priority","Priority","Select",options="Low\nMedium\nHigh\nUrgent",default="Medium",in_list_view=1), field("description","Description","Small Text"), field("attachment","Attachment","Attach"), field("requested_on","Requested On","Datetime",default="Now",read_only=1), field("approvals_section","Approvals","Section Break"), field("manager_approver","Manager Approver","Link",options="User"), field("hr_approver","HR Approver","Link",options="User"), field("resolution","Resolution","Small Text"), field("resolved_on","Resolved On","Datetime",read_only=1)], perms, submit=1)
    ensure_doctype("Employee Data Change Request",[
        field("employee","Employee","Link",options="Employee",reqd=1,in_list_view=1), field("reason","Reason","Small Text",reqd=1), field("requested_on","Requested On","Datetime",default="Now",read_only=1), field("changes","Changes","Table",options="Employee Data Change Request Field",reqd=1), field("approvals_section","Approvals","Section Break"), field("manager_approver","Manager Approver","Link",options="User"), field("hr_approver","HR Approver","Link",options="User"), field("applied_on","Applied On","Datetime",read_only=1), field("apply_error","Apply Error","Small Text",read_only=1)], perms, submit=1)
def ensure_workflows():
    for s in ["Draft","Submitted","Manager Approved","HR Approved","Rejected","Cancelled"]:
        if not frappe.db.exists("Workflow State", s):
            d=frappe.new_doc("Workflow State"); d.workflow_state_name=s; d.insert(ignore_permissions=True)
    for a in ["Submit","Manager Approve","HR Approve","Reject","Cancel"]:
        if not frappe.db.exists("Workflow Action Master", a):
            d=frappe.new_doc("Workflow Action Master"); d.workflow_action_name=a; d.insert(ignore_permissions=True)
    for name,dt in [("HR Request Workflow","HR Request"),("Employee Data Change Request Workflow","Employee Data Change Request")]:
        if frappe.db.exists("Workflow", name): continue
        w=frappe.new_doc("Workflow"); w.workflow_name=name; w.document_type=dt; w.workflow_state_field="workflow_state"; w.is_active=1
        for st,ds in [("Draft",0),("Submitted",1),("Manager Approved",1),("HR Approved",1),("Rejected",1),("Cancelled",2)]: w.append("states",{"state":st,"doc_status":ds,"allow_edit":"HR Admin"})
        for st,act,nxt,role in [("Draft","Submit","Submitted","Employee Self Service"),("Draft","Submit","Submitted","HR Manager"),("Submitted","Manager Approve","Manager Approved","Department Manager"),("Manager Approved","HR Approve","HR Approved","HR Manager"),("Submitted","Reject","Rejected","Department Manager"),("Manager Approved","Reject","Rejected","HR Manager"),("Submitted","Cancel","Cancelled","HR Manager"),("Manager Approved","Cancel","Cancelled","HR Manager")]: w.append("transitions",{"state":st,"action":act,"next_state":nxt,"allowed":role})
        w.insert(ignore_permissions=True)
def run():
    ensure_roles(); ensure_employee_fields(); ensure_doctypes(); ensure_workflows(); frappe.db.commit(); frappe.clear_cache()


def smoke_test():
    from oakglobal_erp_custom.hrms_ext.employee_data_change import apply_approved_changes
    company = frappe.get_all("Company", pluck="name", limit_page_length=1)[0]
    emp = frappe.new_doc("Employee")
    emp.first_name = "Smoke"
    emp.last_name = "HRMS"
    emp.gender = "Male"
    emp.date_of_birth = "1990-01-01"
    emp.date_of_joining = "2026-01-01"
    emp.company = company
    emp.personal_email = "old-smoke@example.com"
    emp.insert(ignore_permissions=True)

    req = frappe.new_doc("Employee Data Change Request")
    req.employee = emp.name
    req.reason = "Smoke test"
    req.append("changes", {"fieldname": "personal_email", "field_label": "Personal Email", "old_value": emp.personal_email, "new_value": "new-smoke@example.com"})
    req.insert(ignore_permissions=True)
    req.workflow_state = "HR Approved"
    apply_approved_changes(req)
    updated = frappe.db.get_value("Employee", emp.name, "personal_email")
    if updated != "new-smoke@example.com":
        raise Exception(f"allowed update failed: {updated}")

    bad = frappe.new_doc("Employee Data Change Request")
    bad.employee = emp.name
    bad.reason = "Smoke test blocked field"
    bad.append("changes", {"fieldname": "salary", "field_label": "Salary", "new_value": "999"})
    bad.insert(ignore_permissions=True)
    bad.workflow_state = "HR Approved"
    try:
        apply_approved_changes(bad)
    except Exception as e:
        if "Field not allowed" not in str(e):
            raise
    else:
        raise Exception("disallowed field was not blocked")
    frappe.db.rollback()
    return "SMOKE_OK"
