# Sprint 17 Reimbursement Preflight Engine

## Goal
Add reimbursement preflight and payroll trace hooks around standard `Expense Claim`.

## Scope
- Runtime module `reimbursement_preflight.py`
- `Expense Claim.validate` hook
- `Expense Claim.on_submit` trace hook when `pay_through_payroll` is enabled
- Checks for missing employee, invalid amount, missing policy, over-limit amount, balance status, and balance availability

## Non-goals
- No payment execution.
- No accounting entry mutation.
- No Expense Claim replacement.
- No payroll formula change.
- No core edits.

## Behavior
- Updates `reimbursement_preflight_status` and `reimbursement_preflight_note`.
- Creates `Payroll Source Trace` for submitted Expense Claim if `pay_through_payroll` is set.
- Avoids duplicate trace rows for same Expense Claim.

## Validation
Run:

```bash
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.reimbursement_preflight.smoke_test
```

Expected:

```text
REIMBURSEMENT_PREFLIGHT_SMOKE_OK
```
