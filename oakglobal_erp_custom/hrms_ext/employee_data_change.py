import frappe

ALLOWED_EMPLOYEE_FIELDS = {
    "personal_email",
    "cell_number",
    "current_address",
    "permanent_address",
    "emergency_phone_number",
    "emergency_contact_relation",
    "bank_account_name",
    "bank_account_no_masked",
}


def apply_approved_changes(doc, method=None):
    if getattr(doc, "workflow_state", None) != "HR Approved":
        return
    if getattr(doc, "applied_on", None):
        return

    employee = frappe.get_doc("Employee", doc.employee)

    for row in doc.changes:
        if row.fieldname not in ALLOWED_EMPLOYEE_FIELDS:
            frappe.throw(f"Field not allowed for employee self-service update: {row.fieldname}")
        employee.set(row.fieldname, row.new_value)

    employee.save(ignore_permissions=True)
    doc.db_set("applied_on", frappe.utils.now(), update_modified=False)
