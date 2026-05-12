"""Sprint 11 ESS/MSS foundation setup and permission helpers."""

from __future__ import annotations

from datetime import date, timedelta

import frappe
from frappe.utils import add_days, getdate, nowdate

APP_MODULE = "Oakglobal ERP Custom"
HR_ROLES = {"HR Admin", "HR Manager", "System Manager"}
MANAGER_ROLE = "Department Manager"
ESS_ROLE = "Employee Self Service"
MAX_ROWS = 500

REPORT_REFS = {
    "Employee Request Center": "Employee",
    "Manager Approval Dashboard": "HR Request",
    "Team Attendance Summary": "Attendance",
    "Team Leave Calendar": "Leave Application",
    "Pending Approval Items": "Workflow Action",
}
REPORTS = list(REPORT_REFS)


def table_exists(doctype: str) -> bool:
    try:
        return bool(frappe.db.table_exists(doctype))
    except Exception:
        return False


def has_column(doctype: str, fieldname: str) -> bool:
    try:
        return bool(table_exists(doctype) and frappe.db.has_column(doctype, fieldname))
    except Exception:
        return False


def user_roles(user: str | None = None) -> set[str]:
    try:
        return set(frappe.get_roles(user or frappe.session.user))
    except Exception:
        return set()


def linked_employee(user: str | None = None) -> str | None:
    user = user or getattr(frappe.session, "user", None)
    if not user or not table_exists("Employee"):
        return None
    try:
        return frappe.db.get_value("Employee", {"user_id": user}, "name")
    except Exception:
        return None


def employee_scope(user: str | None = None, include_manager_reports: bool = True) -> tuple[str, list[str]]:
    """Return scope kind and employee names. HR all. Payroll roles alone get none."""
    roles = user_roles(user)
    if roles & HR_ROLES:
        return "all", []

    employee = linked_employee(user)
    if not employee:
        return "none", []

    allowed = {employee}
    if include_manager_reports and MANAGER_ROLE in roles and has_column("Employee", "reports_to"):
        reports = frappe.get_all("Employee", filters={"reports_to": employee}, pluck="name", limit_page_length=MAX_ROWS)
        allowed.update(reports or [])

    if ESS_ROLE in roles or MANAGER_ROLE in roles:
        return "list", sorted(allowed)
    return "none", []


def employee_condition(alias: str = "employee", user: str | None = None, include_manager_reports: bool = True) -> tuple[str, dict]:
    scope, employees = employee_scope(user, include_manager_reports)
    if scope == "all":
        return "1=1", {}
    if scope == "list" and employees:
        return f"{alias} in %(employees)s", {"employees": tuple(employees)}
    return "1=0", {}


def date_window(filters: dict | None, field: str = "creation") -> tuple[str, str]:
    filters = filters or {}
    to_date = getdate(filters.get("to_date") or nowdate())
    from_date = getdate(filters.get("from_date") or add_days(to_date, -30))
    if from_date > to_date:
        from_date = to_date
    return str(from_date), str(to_date)


def limited(filters: dict | None) -> int:
    try:
        return min(max(int((filters or {}).get("limit") or MAX_ROWS), 1), MAX_ROWS)
    except Exception:
        return MAX_ROWS


def sql_date_clause(field: str, filters: dict | None) -> tuple[str, dict]:
    from_date, to_date = date_window(filters)
    return f"date({field}) between %(from_date)s and %(to_date)s", {"from_date": from_date, "to_date": to_date}


def pending_status_condition(status_field: str = "status", workflow_field: str | None = "workflow_state") -> str:
    parts = [f"coalesce({status_field}, '') in ('Open','Pending','Pending Approval','Applied','Draft')"]
    if workflow_field:
        parts.append(f"coalesce({workflow_field}, '') like '%%Pending%%'")
        parts.append(f"coalesce({workflow_field}, '') like '%%Review%%'")
        parts.append(f"coalesce({workflow_field}, '') like '%%Approval%%'")
    return "(" + " or ".join(parts) + ")"


def ensure_report(name: str) -> None:
    ref_doctype = REPORT_REFS.get(name, "Employee")
    values = {
        "module": APP_MODULE,
        "ref_doctype": ref_doctype,
        "report_type": "Script Report",
        "is_standard": "Yes",
        "disabled": 0,
    }
    if not frappe.db.exists("Report", name):
        doc = frappe.get_doc({
            "doctype": "Report",
            "report_name": name,
            "name": name,
            **values,
        })
        doc.insert(ignore_permissions=True)
    else:
        frappe.db.set_value("Report", name, values)


def ensure_workspace(name: str) -> None:
    if not table_exists("Workspace"):
        return
    values = {
        "label": name,
        "title": name,
        "module": APP_MODULE,
        "public": 0,
    }
    if not frappe.db.exists("Workspace", name):
        frappe.get_doc({
            "doctype": "Workspace",
            "name": name,
            **values,
        }).insert(ignore_permissions=True)
    else:
        frappe.db.set_value("Workspace", name, values)


def run() -> None:
    for report in REPORTS:
        ensure_report(report)
    ensure_workspace("Employee Self Service")
    ensure_workspace("Manager Self Service")


def smoke_test() -> None:
    run()
    for report in REPORTS:
        if not frappe.db.exists("Report", report):
            raise RuntimeError(f"Missing Report: {report}")
    modules = [
        "employee_request_center",
        "manager_approval_dashboard",
        "team_attendance_summary",
        "team_leave_calendar",
        "pending_approval_items",
    ]
    for module in modules:
        mod = __import__(f"oakglobal_erp_custom.report.{module}.{module}", fromlist=["execute"])
        mod.execute({})
    frappe.db.rollback()
