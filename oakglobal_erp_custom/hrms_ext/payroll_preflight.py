"""Payroll preflight checks for Indonesia payroll foundation.

This module does not calculate payroll. It only writes warnings/blockers and summary fields.
"""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

ISSUE_DOCTYPE = "Payroll Preflight Issue"


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


def get_value(doctype: str, name: str | None, fieldname: str):
    if not name or not table_exists(doctype) or not has_column(doctype, fieldname):
        return None
    try:
        return frappe.db.get_value(doctype, name, fieldname)
    except Exception:
        return None


def _append_issue(issues: list[dict], issue_type: str, severity: str, message: str) -> None:
    issues.append({"issue_type": issue_type, "severity": severity, "message": message})


def collect_salary_slip_issues(doc) -> list[dict]:
    issues: list[dict] = []
    employee = getattr(doc, "employee", None)

    if not employee:
        _append_issue(issues, "Other", "Blocker", "Salary Slip has no employee.")
        return issues

    if not getattr(doc, "indonesia_payroll_setting", None):
        _append_issue(issues, "Missing Payroll Setting", "Warning", "Indonesia Payroll Setting is not linked.")

    tax_status = get_value("Employee", employee, "tax_status")
    if not tax_status:
        _append_issue(issues, "Missing Tax Status", "Warning", "Employee tax_status is empty.")

    bpjs_health = get_value("Employee", employee, "bpjs_kesehatan_no")
    bpjs_worker = get_value("Employee", employee, "bpjs_ketenagakerjaan_no")
    if not bpjs_health and not bpjs_worker:
        _append_issue(issues, "Missing BPJS Number", "Warning", "Employee BPJS numbers are empty.")

    if not getattr(doc, "salary_structure", None):
        _append_issue(issues, "Missing Salary Structure", "Blocker", "Salary Slip has no salary structure.")

    if has_column("Salary Slip", "attendance_source_count"):
        count = getattr(doc, "attendance_source_count", None)
        if count in (None, "", 0):
            _append_issue(issues, "Missing Attendance Trace", "Info", "No attendance source trace count on Salary Slip.")

    return issues


def _status_from_issues(issues: list[dict]) -> str:
    severities = {i.get("severity") for i in issues}
    if "Blocker" in severities:
        return "Blocked"
    if "Warning" in severities:
        return "Warning"
    return "Passed"


def _note_from_issues(issues: list[dict]) -> str:
    if not issues:
        return "Payroll preflight passed."
    counts = {}
    for issue in issues:
        counts[issue["severity"]] = counts.get(issue["severity"], 0) + 1
    parts = [f"{k}: {v}" for k, v in sorted(counts.items())]
    return "Payroll preflight issues - " + ", ".join(parts)


def _clear_open_issues(doc) -> None:
    if not table_exists(ISSUE_DOCTYPE) or not getattr(doc, "name", None):
        return
    for name in frappe.get_all(ISSUE_DOCTYPE, filters={"salary_slip": doc.name, "status": "Open"}, pluck="name"):
        frappe.db.set_value(ISSUE_DOCTYPE, name, {"status": "Resolved", "resolved_on": now_datetime()})


def _insert_issues(doc, issues: list[dict]) -> None:
    if not table_exists(ISSUE_DOCTYPE) or not getattr(doc, "name", None):
        return
    for issue in issues:
        frappe.get_doc({
            "doctype": ISSUE_DOCTYPE,
            "payroll_entry": getattr(doc, "payroll_entry", None),
            "salary_slip": doc.name,
            "employee": getattr(doc, "employee", None),
            "issue_type": issue["issue_type"],
            "severity": issue["severity"],
            "status": "Open",
            "message": issue["message"],
            "detected_on": now_datetime(),
        }).insert(ignore_permissions=True)


def run_salary_slip_preflight(doc, persist: bool = True) -> list[dict]:
    issues = collect_salary_slip_issues(doc)
    status = _status_from_issues(issues)
    note = _note_from_issues(issues)

    if has_column("Salary Slip", "payroll_preflight_status"):
        doc.payroll_preflight_status = status
    if has_column("Salary Slip", "payroll_preflight_note"):
        doc.payroll_preflight_note = note

    if persist and getattr(doc, "name", None):
        _clear_open_issues(doc)
        _insert_issues(doc, issues)

    return issues


def validate_salary_slip(doc, method=None) -> None:
    run_salary_slip_preflight(doc, persist=bool(getattr(doc, "name", None)))


def smoke_test() -> str:
    class Dummy:
        doctype = "Salary Slip"
        name = "SMOKE-SALARY-SLIP"
        employee = "SMOKE-EMPLOYEE"
        salary_structure = None
        payroll_entry = None
        indonesia_payroll_setting = None
        attendance_source_count = 0

    doc = Dummy()
    issues = run_salary_slip_preflight(doc, persist=False)
    if not issues:
        raise RuntimeError("Expected preflight issues")
    if doc.payroll_preflight_status != "Blocked":
        raise RuntimeError(f"Unexpected status {doc.payroll_preflight_status}")
    frappe.db.rollback()
    return "PAYROLL_PREFLIGHT_ENGINE_SMOKE_OK"
