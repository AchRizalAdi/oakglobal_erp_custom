# Sprint 3 Attendance/Geofence Foundation Plan

Goal: add Talenta-style attendance location validation foundation while keeping ERPNext/Frappe/HRMS core untouched.

Rules:
- use official HRMS attendance first: Employee Checkin, Attendance, Attendance Request, Shift Type, Shift Assignment
- extend via custom app only
- clean DocType names, no business prefix
- capture audit-friendly evidence: GPS, device, selfie, validation status, distance, reason
- do not calculate payroll yet; Sprint 3 creates source traceability only

Deliverables:
- Attendance Location
- Attendance Geofence
- Attendance Validation Rule
- custom fields on Employee Checkin and Attendance Request
- validation helper with smoke test
- fixtures exported for portability

Core-safe design:
- Attendance Location stores named physical/remote/field work locations.
- Attendance Geofence stores latitude/longitude/radius tied to Attendance Location.
- Attendance Validation Rule stores tolerance and evidence requirements by location/work type.
- Employee Checkin gets captured latitude/longitude, selfie, device metadata, validation status, distance, linked geofence.
- Attendance Request gets geofence exception fields for remote/field/manual approval cases.
