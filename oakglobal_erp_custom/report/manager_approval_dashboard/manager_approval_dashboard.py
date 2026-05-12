import frappe
from oakglobal_erp_custom.hrms_ext.setup_ess_mss import HR_ROLES, MANAGER_ROLE, user_roles

from oakglobal_erp_custom.hrms_ext.setup_ess_mss import employee_condition, has_column, limited, pending_status_condition, table_exists

SOURCES = ["HR Request", "Employee Data Change Request", "Attendance Correction Request", "Shift Change Request", "Leave Application", "Expense Claim", "HR Document Request", "Helpdesk Ticket"]


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Source Doctype", "fieldname": "source_doctype", "fieldtype": "Data", "width": 180},
        {"label": "Source Name", "fieldname": "source_name", "fieldtype": "Dynamic Link", "options": "source_doctype", "width": 180},
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 140},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
        {"label": "Workflow State", "fieldname": "workflow_state", "fieldtype": "Data", "width": 160},
        {"label": "Modified", "fieldname": "modified", "fieldtype": "Datetime", "width": 160},
    ]
    roles = user_roles()
    if not (roles & HR_ROLES or MANAGER_ROLE in roles):
        return columns, []
    cond, params = employee_condition("employee", include_manager_reports=True)
    rows = []
    for dt in SOURCES:
        if not table_exists(dt) or not has_column(dt, "employee"):
            continue
        status = "status" if has_column(dt, "status") else "''"
        workflow = "workflow_state" if has_column(dt, "workflow_state") else "''"
        pending = pending_status_condition(status, workflow if workflow != "''" else None)
        employee_name = "employee_name" if has_column(dt, "employee_name") else "''"
        rows.extend(frappe.db.sql(f"""
            select '{dt}' source_doctype, name source_name, employee, {employee_name} employee_name,
                   {status} status, {workflow} workflow_state, modified
            from `tab{dt}`
            where {cond} and {pending}
            order by modified desc
            limit 500
        """, params, as_dict=True))
    rows.sort(key=lambda d: d.get("modified"), reverse=True)
    return columns, rows[: limited(filters)]
