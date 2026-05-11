# Talenta Feature Gap Map for ERPNext HRMS

Source rulebook: `mekari_talenta_feature_report.md`
Target system: ERPNext/Frappe v16 + HRMS v16 + `oakglobal_erp_custom`
Naming rule: keep DocType/file names clean; do not prefix with `Oak`.

## Legend

Coverage:
- Existing: supported by standard ERPNext/HRMS with configuration.
- Extend: standard DocType exists, needs custom fields/workflow/server logic/report.
- Custom: create new custom DocType/module.
- Later: not MVP.

Priority:
- P0: MVP
- P1: important
- P2: advanced
- P3: AI/optional

---

## Attendance and Time Management

### Online attendance / clock-in/out
- Coverage: Extend
- Existing DocTypes: `Employee Checkin`, `Attendance`
- Needed: source channel, GPS coordinates, selfie/evidence attachment, validation status
- Priority: P0

### GPS geofencing
- Coverage: Custom + Extend
- Existing DocTypes: `Employee Checkin`, `Shift Location`
- New DocTypes: `Geofence Location`, `Attendance Policy`, `Attendance Validation Log`
- Priority: P0

### Face recognition / liveness validation
- Coverage: Later
- Needed now: attachment/evidence and status fields only
- Future: AI/service integration
- Priority: P3

### Live attendance tracking
- Coverage: Custom
- New DocType: `Live Attendance Event`
- Report: `Live Attendance Dashboard`
- Priority: P1

### Timesheet / working hours compliance
- Coverage: Existing + Extend
- Existing DocTypes: `Attendance`, `Shift Type`, `Timesheet`
- Needed: compliance report, late/early/missing checkout flags
- Priority: P0

### Shift management
- Coverage: Existing
- Existing DocTypes: `Shift Type`, `Shift Assignment`, `Shift Request`, `Shift Schedule`
- Needed: approval configuration and reports
- Priority: P0

### Leave / time-off management
- Coverage: Existing
- Existing DocTypes: `Leave Application`, `Leave Allocation`, `Leave Policy`, `Leave Type`
- Needed: workflow/approval polish
- Priority: P0

### Overtime management
- Coverage: Existing + Extend
- Existing DocTypes: `Overtime Slip`, `Overtime Type`, `Overtime Salary Component`
- Needed: request/planning workflow and payroll traceability
- Priority: P0

### Attendance device/fingerprint integration
- Coverage: Custom
- Existing DocType: `Upload Attendance`
- New DocTypes: `Attendance Device`, `Attendance Sync Log`, `External Attendance Import`
- Priority: P1

### Attendance-to-payroll sync
- Coverage: Extend
- Existing DocTypes: `Payroll Entry`, `Salary Slip`, `Additional Salary`, `Overtime Slip`
- New DocType: `Payroll Input Summary`
- Priority: P0

---

## Payroll, Compensation, Benefits

### Payroll calculation
- Coverage: Existing
- Existing DocTypes: `Payroll Entry`, `Salary Structure`, `Salary Slip`, `Salary Component`
- Needed: Indonesian component configuration and audit trail
- Priority: P0

### PPh21 tax calculation
- Coverage: Extend
- Existing DocType: `Income Tax Slab`
- New DocType: `PPh21 Setting`
- Note: validate with Indonesian payroll/accounting expert
- Priority: P1

### BPJS/JHT components
- Coverage: Custom + Existing salary components
- New DocType: `BPJS Setting`
- Priority: P1

### Payroll reporting/audit
- Coverage: Custom + Reports
- New DocTypes: `Payroll Audit Log`, `Payroll Input Summary`
- Priority: P0

### Payroll disbursement
- Coverage: Custom
- New DocType: `Payroll Disbursement Batch`
- Priority: P2

### Payroll cutoff scheduling
- Coverage: Existing + Extend
- Existing DocType: `Payroll Period`
- New DocType: `Payroll Period Rule`
- Priority: P0

### Digital payslip distribution/history
- Coverage: Existing + Extend
- Existing DocType: `Salary Slip`
- New DocType: `Payslip Publish Log`
- Priority: P1

### Reimbursement
- Coverage: Existing + Extend
- Existing DocTypes: `Expense Claim`, `Expense Claim Type`, `Employee Advance`
- Optional Custom: `Reimbursement Policy`, `Reimbursement Balance`
- Priority: P0

### Business travel expense
- Coverage: Existing
- Existing DocTypes: `Travel Request`, `Travel Itinerary`, `Expense Claim`
- Priority: P1

### Employee financial benefits
- Coverage: Existing + Later
- Existing DocTypes: `Employee Benefit Application`, `Employee Benefit Claim`, `Employee Benefit Ledger`
- Priority: P2

### e-Bupot/Coretax integration
- Coverage: Later
- Needed: integration design after payroll rules stable
- Priority: P2

---

## HR Administration / HRIS

### Central employee database/profile
- Coverage: Existing + Extend
- Existing DocType: `Employee`
- Needed: custom fields for local compliance/ops
- Priority: P0

### Organization structure
- Coverage: Existing
- Existing DocTypes: `Company`, `Department`, `Designation`, `Branch`
- Priority: P0

### Employee Self-Service requests
- Coverage: Existing + Custom
- Existing: Leave/Expense/Shift/Attendance requests
- New DocType: `HR Request` for generic ESS
- Priority: P0

### Digital forms and approvals
- Coverage: Custom + Workflow
- New DocTypes: `Employee Data Change Request`, `HR Document Request`
- Priority: P0

### Task/project management
- Coverage: Existing
- Existing DocTypes: `Task`, `Project`, `ToDo`
- Priority: P2

### Internal communication/announcement
- Coverage: Custom
- New DocType: `Announcement`
- Priority: P1

### HR documents/letters
- Coverage: Existing + Custom
- Existing: `Appointment Letter`, print formats
- New DocTypes: `HR Letter Template`, `HR Document Request`
- Priority: P1

### Asset management
- Coverage: Existing ERPNext Assets + Custom HR link
- New DocType: `Asset Assignment` if standard asset assignment not enough
- Priority: P1

### Onboarding/offboarding
- Coverage: Existing + Extend
- Existing DocTypes: `Employee Onboarding`, `Employee Separation`, `Exit Interview`, `Full and Final Statement`
- Needed: checklist templates and asset-return gate
- Priority: P0

### HR helpdesk
- Coverage: Custom or future Helpdesk app
- New DocType: `Helpdesk Ticket`
- Priority: P1

### Activity/audit logs
- Coverage: Existing + Custom
- Existing: `Version`, `Activity Log`, `Audit Trail`
- New: domain audit logs for payroll/attendance
- Priority: P0

---

## Talent Acquisition

### Manpower planning
- Coverage: Existing + Extend
- Existing DocType: `Staffing Plan`, `Job Requisition`
- Needed: approval and link to Job Opening
- Priority: P1

### Recruitment / ATS
- Coverage: Existing
- Existing DocTypes: `Job Opening`, `Job Applicant`, `Interview`, `Job Offer`
- Priority: P1

### AI candidate scoring
- Coverage: Later
- New DocType later: `Recruitment AI Score`
- Priority: P3

### Assessment tests
- Coverage: Extend/Custom
- Existing: `Interview Feedback`
- New DocType: `Applicant Assessment` if needed
- Priority: P1

### Applicant to onboarding
- Coverage: Existing + Extend
- Existing: `Job Applicant`, `Job Offer`, `Employee Onboarding`
- Needed: clean handoff workflow
- Priority: P1

---

## Talent Development

### Performance reviews
- Coverage: Existing
- Existing DocTypes: `Appraisal`, `Appraisal Cycle`, `Appraisal Template`
- Priority: P1

### 360/self/supervisor review
- Coverage: Existing + Extend
- Existing: appraisal/feedback DocTypes
- New DocType if needed: `360 Review`
- Priority: P1

### KPI/OKR/goals
- Coverage: Existing + Extend
- Existing: `Goal`, `KRA`
- New DocType: `OKR Cycle` if OKR needs separate cycle
- Priority: P1

### Competency assessment/maps
- Coverage: Existing + Extend
- Existing: `Skill`, `Employee Skill`, `Employee Skill Map`, `Skill Assessment`
- New DocType: `Competency Map` if needed
- Priority: P1

### Individual Development Plan
- Coverage: Custom
- New DocType: `Individual Development Plan`
- Priority: P1

### Succession planning
- Coverage: Custom
- New DocType: `Succession Plan`
- Priority: P2

### LMS/training
- Coverage: Existing + Extend
- Existing: `Training Program`, `Training Event`, `Training Result`
- New DocTypes later: `Learning Course`, `Learning Enrollment`, `Certificate`
- Priority: P2

---

## AI and Analytics

### HR Analytics dashboards
- Coverage: Reports/Dashboards
- New reports: headcount, attendance, payroll cost, overtime, turnover, performance
- Priority: P1

### Insights+/Pivot Builder
- Coverage: Later
- Build query reports first; pivot/self-service later
- Priority: P2

### HR chatbot / Airene-like assistant
- Coverage: Later
- Needs RBAC-safe query layer
- Priority: P3

### Performance review AI summary
- Coverage: Later
- Priority: P3

### Resignation prediction
- Coverage: Later
- Priority: P3

### Attendance fraud/anomaly detection
- Coverage: Later
- Priority: P3

---

## Integrations and Platform

### Open API
- Coverage: Existing Frappe REST API + Custom
- Needed: documented endpoints and permission roles
- Priority: P1

### Webhooks
- Coverage: Custom/Existing Frappe hooks
- New DocTypes: `Webhook Endpoint`, `Integration Log`
- Priority: P1

### ERP/accounting sync
- Coverage: Existing ERPNext accounting + Extend
- New DocType: `Payroll Journal Mapping`
- Priority: P1

### Device integrations
- Coverage: Custom
- New DocTypes: `Attendance Device`, `Attendance Sync Log`
- Priority: P1

### External product integrations
- Coverage: Later
- Mekari Flex/Expense/Sign equivalents should be internal ERPNext modules first
- Priority: P2

---

## Security and Platform

### RBAC
- Coverage: Existing + Configure
- Existing: Role, DocPerm, User Permission
- Priority: P0

### MFA/security settings
- Coverage: Existing Frappe Security Settings
- Priority: P1

### Audit logs
- Coverage: Existing + Custom domain logs
- Existing: Version, Activity Log, Audit Trail
- New: Payroll/Attendance audit logs
- Priority: P0

### Data ownership/export
- Coverage: Existing Data Export + custom reports
- Priority: P1

---

## MVP Build List

Build first:
1. fixtures config in `hooks.py`
2. roles and permissions
3. Employee custom fields
4. `HR Request`
5. `Employee Data Change Request`
6. `Geofence Location`
7. `Attendance Policy`
8. `Attendance Validation Log`
9. `Payroll Input Summary`
10. `Payroll Audit Log`
11. `Reimbursement Policy` only if `Expense Claim` cannot satisfy needs
12. basic dashboards/reports

Do not build first:
- AI chatbot
- resignation prediction
- Coretax/e-Bupot
- full LMS
- succession planning
- mobile app clone

---

## Immediate Next Step

Create exact implementation plan for Sprint 2:
- add fixtures list to `hooks.py`
- define roles
- define Employee custom fields
- define `HR Request`
- define `Employee Data Change Request`
- define workflows
- include tests/verification commands
