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
        {"label": "Attendance Date", "fieldname": "attendance_date", "fieldtype": "Date", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "In Time", "fieldname": "in_time", "fieldtype": "Datetime", "width": 160},
        {"label": "Out Time", "fieldname": "out_time", "fieldtype": "Datetime", "width": 160},
    ]
    if not table_exists("Attendance") or not has_column("Attendance", "employee"):
        return columns, []
    cond, params = employee_condition("a.employee", include_manager_reports=True)
    from_date, to_date = date_window(filters)
    params.update({"from_date": from_date, "to_date": to_date})
    employee_name = "a.employee_name" if has_column("Attendance", "employee_name") else "''"
    att_date = "a.attendance_date" if has_column("Attendance", "attendance_date") else "date(a.creation)"
    status = "a.status" if has_column("Attendance", "status") else "''"
    join = ""
    select_checkin = "null as in_time, null as out_time"
    if table_exists("Employee Checkin") and has_column("Employee Checkin", "employee") and has_column("Employee Checkin", "time"):
        join = f"""
            left join (
                select employee, date(time) checkin_date, min(time) in_time, max(time) out_time
                from `tabEmployee Checkin`
                where date(time) between %(from_date)s and %(to_date)s
                group by employee, date(time)
            ) c on c.employee = a.employee and c.checkin_date = {att_date}
        """
        select_checkin = "c.in_time, c.out_time"
    rows = frappe.db.sql(f"""
        select a.employee, {employee_name} employee_name, {att_date} attendance_date,
               {status} status, {select_checkin}
        from `tabAttendance` a
        {join}
        where {cond} and {att_date} between %(from_date)s and %(to_date)s
        order by attendance_date desc, employee asc
        limit {limited(filters)}
    """, params, as_dict=True)
    return columns, rows
