# Sprint 18 Benefits Foundation

## Goal
Add benefits policy and utilization tracking while keeping official HRMS benefit DocTypes as base.

## Scope
- Custom DocType `Benefit Policy`
- Custom DocType `Benefit Utilization Log`
- Custom fields on official `Employee Benefit Application`
- Custom fields on official `Employee Benefit Claim`
- Fixture filters updated

## Non-goals
- No replacement of official HRMS benefit DocTypes.
- No payroll formula changes.
- No benefit payout execution.
- No ERPNext/HRMS core edits.

## Controls
- `Benefit Policy` stores type, effective dates, limits, approval flag, taxable flag, and payroll component link.
- `Benefit Utilization Log` tracks usage/reservation/paid/cancelled states.
- HRMS official benefit application/claim records stay canonical request documents.

## Validation
Run:

```bash
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_benefits.smoke_test
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_benefits.run
bench --site erp.localhost export-fixtures
```

Expected:

```text
BENEFITS_SETUP_SMOKE_OK
```
