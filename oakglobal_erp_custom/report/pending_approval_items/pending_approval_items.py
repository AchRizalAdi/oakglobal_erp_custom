import frappe

from oakglobal_erp_custom.hrms_ext.setup_ess_mss import limited, table_exists, has_column


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Reference Doctype", "fieldname": "reference_doctype", "fieldtype": "Data", "width": 180},
        {"label": "Reference Name", "fieldname": "reference_name", "fieldtype": "Dynamic Link", "options": "reference_doctype", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Workflow State", "fieldname": "workflow_state", "fieldtype": "Data", "width": 160},
        {"label": "Creation", "fieldname": "creation", "fieldtype": "Datetime", "width": 160},
    ]
    if not table_exists("Workflow Action"):
        return columns, []
    ref_dt = "reference_doctype" if has_column("Workflow Action", "reference_doctype") else None
    ref_name = "reference_name" if has_column("Workflow Action", "reference_name") else None
    if not ref_dt or not ref_name:
        return columns, []
    user_field = "user" if has_column("Workflow Action", "user") else None
    status = "status" if has_column("Workflow Action", "status") else "''"
    workflow_state = "workflow_state" if has_column("Workflow Action", "workflow_state") else "''"
    if not user_field:
        return columns, []
    cond = "user = %(user)s"
    params = {"user": frappe.session.user}
    if status != "''":
        cond += " and coalesce(status, '') in ('Open','Pending')"
    rows = frappe.db.sql(f"""
        select {ref_dt} reference_doctype, {ref_name} reference_name,
               {status} status, {workflow_state} workflow_state, creation
        from `tabWorkflow Action`
        where {cond}
        order by creation desc
        limit {limited(filters)}
    """, params, as_dict=True)
    return columns, rows
