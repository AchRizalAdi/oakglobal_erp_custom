import frappe

from oakglobal_erp_custom.hrms_ext.setup_payroll_controls import can_view_payroll, has_column, limited, table_exists


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Severity", "fieldname": "severity", "fieldtype": "Data", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Issue Type", "fieldname": "issue_type", "fieldtype": "Data", "width": 220},
        {"label": "Issue Count", "fieldname": "issue_count", "fieldtype": "Int", "width": 120},
        {"label": "Employees", "fieldname": "employee_count", "fieldtype": "Int", "width": 120},
        {"label": "Latest Detected", "fieldname": "latest_detected_on", "fieldtype": "Datetime", "width": 170},
    ]
    if not can_view_payroll() or not table_exists("Payroll Preflight Issue"):
        return columns, []
    needed = ["severity", "status", "issue_type", "employee", "detected_on"]
    if not all(has_column("Payroll Preflight Issue", f) for f in needed):
        return columns, []
    cond = []
    params = {}
    if filters.get("severity"):
        cond.append("severity = %(severity)s")
        params["severity"] = filters.get("severity")
    if filters.get("status"):
        cond.append("status = %(status)s")
        params["status"] = filters.get("status")
    where = "where " + " and ".join(cond) if cond else ""
    rows = frappe.db.sql(f"""
        select severity, status, issue_type,
               count(*) issue_count,
               count(distinct employee) employee_count,
               max(detected_on) latest_detected_on
        from `tabPayroll Preflight Issue`
        {where}
        group by severity, status, issue_type
        order by field(severity, 'Blocker', 'Warning', 'Info'), issue_count desc
        limit {limited(filters)}
    """, params, as_dict=True)
    return columns, rows
