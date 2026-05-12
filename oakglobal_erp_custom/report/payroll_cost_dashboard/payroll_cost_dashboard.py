import frappe

from oakglobal_erp_custom.hrms_ext.setup_payroll_controls import can_view_payroll, has_column, limited, table_exists


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 180},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 110},
        {"label": "End Date", "fieldname": "end_date", "fieldtype": "Date", "width": 110},
        {"label": "Slip Count", "fieldname": "slip_count", "fieldtype": "Int", "width": 100},
        {"label": "Employees", "fieldname": "employee_count", "fieldtype": "Int", "width": 100},
        {"label": "Gross Pay", "fieldname": "gross_pay", "fieldtype": "Currency", "width": 130},
        {"label": "Net Pay", "fieldname": "net_pay", "fieldtype": "Currency", "width": 130},
        {"label": "Rounded Total", "fieldname": "rounded_total", "fieldtype": "Currency", "width": 130},
        {"label": "Preflight Status", "fieldname": "payroll_preflight_status", "fieldtype": "Data", "width": 140},
    ]
    if not can_view_payroll() or not table_exists("Salary Slip"):
        return columns, []
    needed = ["company", "start_date", "end_date", "employee", "gross_pay", "net_pay", "rounded_total"]
    if not all(has_column("Salary Slip", f) for f in needed):
        return columns, []
    preflight = "payroll_preflight_status" if has_column("Salary Slip", "payroll_preflight_status") else "'Not Checked'"
    cond = []
    params = {}
    if filters.get("company"):
        cond.append("company = %(company)s")
        params["company"] = filters.get("company")
    if filters.get("from_date"):
        cond.append("start_date >= %(from_date)s")
        params["from_date"] = filters.get("from_date")
    if filters.get("to_date"):
        cond.append("end_date <= %(to_date)s")
        params["to_date"] = filters.get("to_date")
    where = "where " + " and ".join(cond) if cond else ""
    rows = frappe.db.sql(f"""
        select company, start_date, end_date,
               count(*) slip_count,
               count(distinct employee) employee_count,
               sum(coalesce(gross_pay, 0)) gross_pay,
               sum(coalesce(net_pay, 0)) net_pay,
               sum(coalesce(rounded_total, 0)) rounded_total,
               {preflight} payroll_preflight_status
        from `tabSalary Slip`
        {where}
        group by company, start_date, end_date, {preflight}
        order by end_date desc, company
        limit {limited(filters)}
    """, params, as_dict=True)
    return columns, rows
