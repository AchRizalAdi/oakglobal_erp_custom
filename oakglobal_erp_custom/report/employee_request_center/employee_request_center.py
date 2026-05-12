import frappe

from oakglobal_erp_custom.hrms_ext.setup_ess_mss import (
    MAX_ROWS,
    date_window,
    employee_condition,
    has_column,
    limited,
    table_exists,
)

SOURCES = [
    ("HR Request", "request_type", "subject"),
    ("Employee Data Change Request", None, "subject"),
    ("Attendance Correction Request", None, "reason"),
    ("Shift Change Request", None, "reason"),
    ("Leave Application", "leave_type", "description"),
    ("Expense Claim", None, "remark"),
    ("HR Document Request", "document_type", "subject"),
    ("Helpdesk Ticket", None, "subject"),
]


def columns():
    return [
        {"label": "Source Doctype", "fieldname": "source_doctype", "fieldtype": "Data", "width": 180},
        {"label": "Source Name", "fieldname": "source_name", "fieldtype": "Dynamic Link", "options": "source_doctype", "width": 180},
        {"label": "Request Type", "fieldname": "request_type", "fieldtype": "Data", "width": 160},
        {"label": "Subject", "fieldname": "subject", "fieldtype": "Data", "width": 240},
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 140},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
        {"label": "Workflow State", "fieldname": "workflow_state", "fieldtype": "Data", "width": 160},
        {"label": "Creation", "fieldname": "creation", "fieldtype": "Datetime", "width": 160},
        {"label": "Modified", "fieldname": "modified", "fieldtype": "Datetime", "width": 160},
        {"label": "Owner", "fieldname": "owner", "fieldtype": "Data", "width": 180},
    ]


def field_expr(doctype, fieldname, fallback="''"):
    return f"`tab{doctype}`.`{fieldname}`" if fieldname and has_column(doctype, fieldname) else fallback


def execute(filters=None):
    filters = filters or {}
    from_date, to_date = date_window(filters)
    cond, params = employee_condition("employee", include_manager_reports=False)
    params.update({"from_date": from_date, "to_date": to_date})
    rows = []
    for doctype, request_field, subject_field in SOURCES:
        if not table_exists(doctype) or not has_column(doctype, "employee"):
            continue
        status = field_expr(doctype, "status")
        workflow = field_expr(doctype, "workflow_state")
        subject = field_expr(doctype, subject_field)
        request_type = field_expr(doctype, request_field, f"'{doctype}'")
        employee_name = field_expr(doctype, "employee_name")
        sql = f"""
            select '{doctype}' as source_doctype, name as source_name,
                   {request_type} as request_type, {subject} as subject,
                   employee, {employee_name} as employee_name,
                   {status} as status, {workflow} as workflow_state,
                   creation, modified, owner
            from `tab{doctype}`
            where {cond} and date(creation) between %(from_date)s and %(to_date)s
            order by modified desc
            limit {MAX_ROWS}
        """
        rows.extend(frappe.db.sql(sql, params, as_dict=True))
    rows.sort(key=lambda d: d.get("modified") or d.get("creation"), reverse=True)
    return columns(), rows[: limited(filters)]
