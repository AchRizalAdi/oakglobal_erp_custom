# Sprint 5 Attendance Approval and Audit

Goal: add audit trail and exception approval for attendance validation without touching ERPNext/Frappe/HRMS core.

Deliverables:
- `Attendance Validation Log` records validation output for each Employee Checkin.
- `Attendance Validation Exception` tracks approval for Manual Review, Outside Geofence, or Missing Location.
- Employee Checkin links to exception and override status.
- Helper functions create, approve, and reject exceptions.

Scope:
- no payroll formula changes
- no salary slip mutation
- no HRMS core edits

Smoke tests:
- outside geofence checkin is flagged
- validation log is created
- exception approval updates Employee Checkin override status
