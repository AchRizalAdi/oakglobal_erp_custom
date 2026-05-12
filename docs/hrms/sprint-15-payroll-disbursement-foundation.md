# Sprint 15 Payroll Disbursement Foundation

## Goal
Add safe payroll disbursement records for approval/export tracking without sending money or changing payroll formulas.

## Scope
- Custom child DocType `Payroll Disbursement Line`
- Custom DocType `Payroll Disbursement Batch`
- Custom DocType `Payroll Bank Export Log`
- Fixture filters updated for DocType and permissions

## Non-goals
- No bank API integration.
- No automatic payment execution.
- No salary calculation changes.
- No ERPNext/HRMS core edits.

## Controls
- Batch is submittable for audit.
- Lines store employee, salary slip, masked bank account, amount, and payment status.
- Export log records who generated/exported file and status.
- Bank account number remains masked only.

## Validation
Run:

```bash
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_payroll_disbursement.smoke_test
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_payroll_disbursement.run
bench --site erp.localhost export-fixtures
```

Expected:

```text
PAYROLL_DISBURSEMENT_SETUP_SMOKE_OK
```
