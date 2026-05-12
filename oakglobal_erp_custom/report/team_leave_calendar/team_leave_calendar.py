import frappe
from oakglobal_erp_custom.hrms_ext.setup_ess_mss import HR_ROLES, MANAGER_ROLE, user_roles

from oakglobal_erp_custom.hrms_ext.setup_ess_mss import date_window, employee_condition, has_column, limited, table_exists


def execute(filters=None):
    filters = filters or {}

    roles = user_roles()
    if not (roles & HR_ROLES or MANAGER_ROLE in roles):
        return columns, []
    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 140},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
        {"label": "Leave Type", "fieldname": "leave_type", "fieldtype": "Data", "width": 150},
        {"label": "From Date", "fieldname": "from_date", "fieldtype": "Date", "width": 120},
        {"label": "To Date", "fieldname": "to_date", "fieldtype": "Date", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]
    if not table_exists("Leave Application") or not has_column("Leave Application", "employee"):
        return columns, []
    cond, params = employee_condition("employee", include_manager_reports=True)
    from_date, to_date = date_window(filters)
    params.update({"from_date": from_date, "to_date": to_date})
    employee_name = "employee_name" if has_column("Leave Application", "employee_name") else "''"
    leave_type = "leave_type" if has_column("Leave Application", "leave_type") else "''"
    status = "status" if has_column("Leave Application", "status") else "''"
    fd = "from_date" if has_column("Leave Application", "from_date") else "date(creation)"
    td = "to_date" if has_column("Leave Application", "to_date") else fd
    rows = frappe.db.sql(f"""
        select employee, {employee_name} employee_name, {leave_type} leave_type,
               {fd} from_date, {td} to_date, {status} status
        from `tabLeave Application`
        where {cond} and {fd} <= %(to_date)s and {td} >= %(from_date)s
        order by {fd} asc, employee asc
        limit {limited(filters)}
    """, params, as_dict=True)
    return columns, rows
