"""Sprint 13 payroll controls reports setup."""

import frappe

APP_MODULE = "Oakglobal ERP Custom"
PAYROLL_ROLES = {"Payroll Manager", "Payroll User", "System Manager"}
REPORT_REFS = {
    "Payroll Preflight Summary": "Payroll Preflight Issue",
    "Payroll Cost Dashboard": "Salary Slip",
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


def can_view_payroll(user: str | None = None) -> bool:
    return bool(user_roles(user) & PAYROLL_ROLES)


def limited(filters: dict | None, default: int = 500) -> int:
    try:
        return min(max(int((filters or {}).get("limit") or default), 1), 1000)
    except Exception:
        return default


def ensure_report(name: str) -> None:
    values = {
        "module": APP_MODULE,
        "ref_doctype": REPORT_REFS.get(name, "Salary Slip"),
        "report_type": "Script Report",
        "is_standard": "Yes",
        "disabled": 0,
    }
    if not frappe.db.exists("Report", name):
        frappe.get_doc({"doctype": "Report", "report_name": name, "name": name, **values}).insert(ignore_permissions=True)
    else:
        frappe.db.set_value("Report", name, values)


def run() -> None:
    for report in REPORTS:
        ensure_report(report)
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test() -> str:
    run()
    for report in REPORTS:
        if not frappe.db.exists("Report", report):
            raise RuntimeError(f"Missing Report: {report}")
    for module in ["payroll_preflight_summary", "payroll_cost_dashboard"]:
        mod = __import__(f"oakglobal_erp_custom.report.{module}.{module}", fromlist=["execute"])
        mod.execute({})
    frappe.db.rollback()
    return "PAYROLL_CONTROLS_SETUP_SMOKE_OK"
