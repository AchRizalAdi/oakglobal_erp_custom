# Sprint 12 Indonesia Payroll Foundation

## Goal
Add core-safe Indonesia payroll configuration foundation for BPJS, PPh 21, THR, and payroll preflight checks.

## Scope
- Custom DocType `Indonesia Payroll Setting`
- Custom DocType `BPJS Profile`
- Custom DocType `PPh21 Profile`
- Custom DocType `THR Rule`
- Custom DocType `Payroll Preflight Issue`
- `Salary Slip` custom fields linking payroll setting/profile/rule and preflight status

## Non-goals
- No salary formula changes.
- No tax calculation engine yet.
- No Coretax/e-Bupot integration.
- No bank disbursement flow.
- No ERPNext/HRMS core edits.

## Controls
- Payroll roles own setup data.
- HR Admin read-only visibility only.
- Effective dates kept explicit for audit.
- Payroll preflight issue model separates warning/blocker checks from payroll calculation.

## Validation
Run:

```bash
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_indonesia_payroll.smoke_test
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_indonesia_payroll.run
bench --site erp.localhost export-fixtures
```

Expected smoke result:

```text
INDONESIA_PAYROLL_SETUP_SMOKE_OK
```
