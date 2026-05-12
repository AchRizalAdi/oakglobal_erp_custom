# Sprint 13 Payroll Controls Reports

## Goal
Add payroll visibility and control reports without changing payroll calculation formulas.

## Scope
- Script Report `Payroll Preflight Summary`
- Script Report `Payroll Cost Dashboard`
- Setup module `setup_payroll_controls.py`
- Fixture filters updated for report export

## Controls
- Payroll reports are server-gated to Payroll Manager, Payroll User, and System Manager.
- HR roles do not automatically see payroll cost data.
- Reports return empty when required DocTypes/columns are missing.
- No ERPNext/HRMS core edits.

## Non-goals
- No PPh 21 engine.
- No BPJS calculation engine.
- No THR generation.
- No payroll disbursement.

## Validation
Run:

```bash
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_payroll_controls.smoke_test
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_payroll_controls.run
bench --site erp.localhost export-fixtures
```

Expected smoke result:

```text
PAYROLL_CONTROLS_SETUP_SMOKE_OK
```
