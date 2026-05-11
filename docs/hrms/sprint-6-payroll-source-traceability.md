# Sprint 6 Payroll Source Traceability

Goal: add payroll source trace foundation without changing payroll formulas or HRMS core.

Deliverables:
- `Payroll Source Trace` DocType records source records that can affect payroll.
- Salary Slip gets read-only trace summary fields.
- Helper creates traces from Employee Checkin and Attendance Validation Exception for a period.

Scope:
- no salary formula changes
- no automatic salary slip mutation unless helper explicitly called
- core untouched

Smoke tests:
- setup creates DocType and Salary Slip fields
- attendance checkin and approved exception produce trace records
