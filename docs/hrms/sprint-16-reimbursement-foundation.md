# Sprint 16 Reimbursement Foundation

## Goal
Add reimbursement policy, balance, and payout tracking around standard ERPNext `Expense Claim`.

## Scope
- Custom DocType `Reimbursement Policy`
- Custom DocType `Reimbursement Balance`
- Custom DocType `Reimbursement Disbursement Log`
- Custom fields on `Expense Claim`
- Fixture filters updated

## Non-goals
- No replacement of standard `Expense Claim`.
- No bank transfer execution.
- No payroll formula changes.
- No ERPNext/HRMS core edits.

## Controls
- Standard `Expense Claim` remains base request document.
- Policy controls limit, receipt requirement, over-limit approval flag, and payroll payout flag.
- Balance tracks opening/used/reserved/available values for audit.
- Disbursement log links approved claim to payroll/bank/cash payout tracking.

## Validation
Run:

```bash
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_reimbursement.smoke_test
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_reimbursement.run
bench --site erp.localhost export-fixtures
```

Expected:

```text
REIMBURSEMENT_SETUP_SMOKE_OK
```
