"""Reimbursement preflight and trace helpers.

No payment execution. No accounting mutation. Only flags and trace records.
"""

from __future__ import annotations

import frappe
from frappe.utils import flt, getdate


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


def _get_value(doctype: str, name: str | None, fieldname: str):
    if not name or not table_exists(doctype) or not has_column(doctype, fieldname):
        return None
    try:
        return frappe.db.get_value(doctype, name, fieldname)
    except Exception:
        return None


def _append(issues: list[dict], issue_type: str, severity: str, message: str) -> None:
    issues.append({"issue_type": issue_type, "severity": severity, "message": message})


def _claim_amount(doc) -> float:
    for fieldname in ("total_sanctioned_amount", "total_claimed_amount", "grand_total"):
        value = flt(getattr(doc, fieldname, 0))
        if value:
            return value
    return 0.0


def collect_expense_claim_issues(doc) -> list[dict]:
    issues: list[dict] = []
    amount = _claim_amount(doc)
    policy = getattr(doc, "reimbursement_policy", None)
    balance = getattr(doc, "reimbursement_balance", None)

    if not getattr(doc, "employee", None):
        _append(issues, "Missing Employee", "Blocker", "Expense Claim has no employee.")
    if amount <= 0:
        _append(issues, "Invalid Amount", "Blocker", "Expense Claim amount is zero or negative.")
    if not policy:
        _append(issues, "Missing Policy", "Warning", "Reimbursement Policy is not linked.")

    if policy:
        limit_amount = flt(_get_value("Reimbursement Policy", policy, "limit_amount"))
        requires_receipt = bool(_get_value("Reimbursement Policy", policy, "requires_receipt"))
        if limit_amount and amount > limit_amount:
            _append(issues, "Over Limit", "Warning", f"Claim amount {amount} exceeds policy limit {limit_amount}.")
        if requires_receipt and not getattr(doc, "remarks", None) and not getattr(doc, "remark", None):
            _append(issues, "Missing Receipt Note", "Info", "Policy requires receipt; ensure attachment or note is present.")

    if balance:
        available = flt(_get_value("Reimbursement Balance", balance, "available_balance"))
        status = _get_value("Reimbursement Balance", balance, "status")
        if status and status != "Open":
            _append(issues, "Balance Closed", "Blocker", f"Reimbursement balance status is {status}.")
        if available and amount > available:
            _append(issues, "Insufficient Balance", "Warning", f"Claim amount {amount} exceeds available balance {available}.")

    if getattr(doc, "pay_through_payroll", None) and not table_exists("Payroll Source Trace"):
        _append(issues, "Missing Payroll Trace", "Warning", "Payroll Source Trace is unavailable.")

    return issues


def _status_from_issues(issues: list[dict]) -> str:
    severities = {i["severity"] for i in issues}
    if "Blocker" in severities:
        return "Blocked"
    if "Warning" in severities:
        return "Warning"
    return "Passed"


def _note_from_issues(issues: list[dict]) -> str:
    if not issues:
        return "Reimbursement preflight passed."
    counts = {}
    for issue in issues:
        counts[issue["severity"]] = counts.get(issue["severity"], 0) + 1
    return "Reimbursement preflight issues - " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))


def run_expense_claim_preflight(doc) -> list[dict]:
    issues = collect_expense_claim_issues(doc)
    if has_column("Expense Claim", "reimbursement_preflight_status"):
        doc.reimbursement_preflight_status = _status_from_issues(issues)
    if has_column("Expense Claim", "reimbursement_preflight_note"):
        doc.reimbursement_preflight_note = _note_from_issues(issues)
    return issues


def validate_expense_claim(doc, method=None) -> None:
    run_expense_claim_preflight(doc)


def create_payroll_trace_for_claim(doc, method=None) -> None:
    if not getattr(doc, "pay_through_payroll", None):
        return
    if not table_exists("Payroll Source Trace"):
        return
    if frappe.db.exists("Payroll Source Trace", {"source_doctype": "Expense Claim", "source_name": doc.name}):
        return
    amount = _claim_amount(doc)
    source_date = getdate(getattr(doc, "posting_date", None) or frappe.utils.nowdate())
    frappe.get_doc({
        "doctype": "Payroll Source Trace",
        "employee": getattr(doc, "employee", None),
        "company": getattr(doc, "company", None),
        "period_start": source_date,
        "period_end": source_date,
        "source_type": "Expense Claim",
        "source_doctype": "Expense Claim",
        "source_name": doc.name,
        "source_date": source_date,
        "source_status": getattr(doc, "approval_status", None) or getattr(doc, "status", None),
        "quantity": 1,
        "amount": amount,
        "trace_note": "Expense Claim marked pay through payroll.",
    }).insert(ignore_permissions=True)


def smoke_test() -> str:
    class Dummy:
        doctype = "Expense Claim"
        name = "SMOKE-EXPENSE-CLAIM"
        employee = None
        company = None
        posting_date = None
        reimbursement_policy = None
        reimbursement_balance = None
        total_sanctioned_amount = 0
        total_claimed_amount = 0
        grand_total = 0
        pay_through_payroll = 1

    doc = Dummy()
    issues = run_expense_claim_preflight(doc)
    if not issues:
        raise RuntimeError("Expected reimbursement issues")
    if doc.reimbursement_preflight_status != "Blocked":
        raise RuntimeError(f"Unexpected status {doc.reimbursement_preflight_status}")
    frappe.db.rollback()
    return "REIMBURSEMENT_PREFLIGHT_SMOKE_OK"
