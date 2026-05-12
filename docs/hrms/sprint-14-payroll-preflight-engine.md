# Sprint 14 Payroll Preflight Engine

## Goal
Add a safe payroll preflight engine that flags missing setup before payroll is trusted.

## Scope
- Runtime module `payroll_preflight.py`
- Salary Slip validation hook
- Checks for:
  - missing Indonesia payroll setting
  - missing employee tax status
  - missing BPJS numbers
  - missing salary structure
  - missing attendance trace count
- Updates Salary Slip preflight summary fields
- Creates/resolves `Payroll Preflight Issue` rows when Salary Slip has a saved name

## Non-goals
- No payroll amount calculation.
- No BPJS calculation.
- No PPh 21 calculation.
- No THR calculation.
- No core edits.

## Behavior
- Blocker if salary structure missing.
- Warning if payroll setting, tax status, or BPJS identity is missing.
- Info if attendance trace is missing.
- Existing open issues for the slip are marked resolved before new open issues are written.

## Validation
Run:

```bash
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.payroll_preflight.smoke_test
```

Expected:

```text
PAYROLL_PREFLIGHT_ENGINE_SMOKE_OK
```
