# Sprint 4 Attendance Validation Automation

Goal: automate Attendance/geofence validation on Employee Checkin without touching ERPNext/Frappe/HRMS core.

Rules:
- use `Employee Checkin` validate hook from custom app
- use Sprint 3 `Attendance Location`, `Attendance Geofence`, `Attendance Validation Rule`
- compute distance from captured GPS to active geofence
- set validation status and message before save
- route exceptions to Manual Review or Outside Geofence; do not block payroll yet

Statuses:
- Pending: no attendance location selected
- Valid: inside radius
- Outside Geofence: outside radius and not allowed by rule
- Missing Location: GPS missing
- Manual Review: missing geofence, selfie required, or allowed outside geofence

Smoke tests:
- inside point becomes Valid
- outside point becomes Outside Geofence
- missing GPS becomes Missing Location
