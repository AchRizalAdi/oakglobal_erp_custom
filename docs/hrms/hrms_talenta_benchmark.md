# ERPNext HRMS Benchmark Against Talenta-Inspired HRIS/HCM PRD

Source PRD: `prd_hris_hcm_talenta_inspired.md`
Target stack: ERPNext/Frappe v16 + HRMS v16 + `oakglobal_erp_custom`
Local environment: WSL `rijoll`, project `oaklocal`, site `erp.localhost`
Status: planning benchmark

## Executive summary

ERPNext HRMS is a strong base for an Indonesian HRIS/HCM product, but it is not a Talenta-equivalent SaaS out of the box.

Best use:
- Treat ERPNext/HRMS as stable core for employee data, leave, attendance, payroll documents, expense claim, recruitment basics, performance basics, workflow, role permission, audit, and API foundation.
- Build Talenta-like coverage in `oakglobal_erp_custom` through custom fields, custom DocTypes, workflows, reports, dashboards, hooks, API wrappers, and integrations.
- Keep ERPNext/Frappe/HRMS core untouched.

Highest gaps:
- Mobile-first employee experience.
- GPS/geofence/face/liveness attendance controls.
- Indonesia payroll localization depth: PPh 21, BPJS, THR, Coretax/e-Bupot, auditability.
- Manager self-service dashboards.
- Productized analytics.
- AI HR assistant with permission-safe data access.
- Enterprise integrations and webhook product layer.

## Fit score summary

- Core HR / employee database: 80%
- Organization structure: 75%
- Role and permission management: 85%
- Employee self-service: 60%
- Manager self-service: 55%
- Mobile attendance: 45%
- GPS/geofence attendance: 45% after current custom foundation, lower without it
- Face recognition / liveness: 15%
- Shift management: 65%
- Leave / time-off: 80%
- Overtime management: 60%
- Timesheet: 65%
- Payroll management: 60% generic, 35-45% Indonesia-ready without custom localization
- PPh 21 / BPJS: 35%
- Digital payslip: 70%
- Reimbursement / expense: 70%
- HR document management: 45%
- Asset management: 50%
- Onboarding / offboarding: 55%
- Recruitment / ATS: 55%
- Manpower planning: 50%
- Performance management: 55%
- KPI / OKR: 45%
- Talent management: 30%
- LMS: 25%
- HR analytics and dashboard: 40%
- AI HR assistant: 10%
- Open API: 75% platform base, 45% productized API
- Webhook: 60% platform base, 35% productized events
- Audit log and security: 75%

## Mapping by PRD module

### 1. Core HR / Employee Database

ERPNext/HRMS coverage:
- `Employee`
- `Company`
- `Department`
- `Designation`
- `Branch`
- employee status fields
- attachments
- standard import/export
- version/audit trail foundation

Gap:
- richer employee profile sections may need custom fields.
- Talenta-like profile UX and mobile profile editing are not native.
- employee data change approval needs productized flow.

Recommended implementation:
- Extend `Employee` with custom fields only where standard fields are missing.
- Use existing employee lifecycle/status fields where possible.
- Add `Employee Data Change Request` for employee-submitted profile changes.
- Export custom fields and workflows as fixtures.

Priority:
- P0.

### 2. Organization Structure

ERPNext/HRMS coverage:
- company, branch, department, designation, reports-to relationship.

Gap:
- org chart UX and advanced multi-entity permissions need polish.
- branch/department-scoped dashboards need custom reports.

Recommended implementation:
- Use standard org entities.
- Add reports for headcount by branch, department, status, employment type.
- Use Role Permission Manager and User Permission records for branch/department scoping.

Priority:
- P0.

### 3. Role and Permission Management

ERPNext/Frappe coverage:
- role-based access control.
- user permissions.
- document permissions.
- workflow permissions.
- audit/version logs.

Gap:
- PRD requires role + department + branch + reporting-line access. Reporting-line filtering often needs custom query conditions.
- AI permission boundary must be built separately.

Recommended implementation:
- Use standard roles for HR Admin, Payroll Admin, Manager, Employee, Management.
- Add permission query hooks only where standard permission cannot express team access.
- Keep permission matrix documented and tested.

Priority:
- P0.

### 4. Employee Self-Service

ERPNext/HRMS coverage:
- employee can access leave, expense claim, salary slips, some requests depending roles.
- workflow and notifications exist.

Gap:
- Talenta-style request center and mobile app UX are missing.
- unified status tracking for leave, overtime, reimbursement, attendance correction, shift change, and data change needs custom layer.

Recommended implementation:
- Build ESS workspace/pages first inside Frappe Desk or website/PWA.
- Add generic `HR Request` only for gaps that do not map to official DocTypes.
- Use official DocTypes for leave, overtime, expense claim, shift request where possible.

Priority:
- P0.

### 5. Manager Self-Service

ERPNext/HRMS coverage:
- managers can approve workflow documents if configured.
- reports can be scoped by permissions.

Gap:
- team dashboard, approval inbox, attendance live view, leave calendar, overtime cost view need custom reports/pages.

Recommended implementation:
- Add Manager Dashboard workspace.
- Add query reports: team attendance, team leave calendar, team overtime, pending approvals.
- Add permission filtering by reports-to chain.

Priority:
- P0/P1.

### 6. Attendance Management

ERPNext/HRMS coverage:
- `Employee Checkin`
- `Attendance`
- `Attendance Request`
- `Shift Type`
- auto attendance support
- upload attendance support

Gap:
- mobile capture flow is not complete.
- GPS/geofence validation needs custom logic.
- face recognition/liveness not native.
- live attendance dashboard needs custom report/event tracking.
- attendance correction needs workflow polish.

Current/custom foundation expected:
- geofence/location/policy foundation in custom app.
- employee checkin validation hooks.
- validation audit and exception approval.

Recommended implementation:
- Extend `Employee Checkin` with captured latitude, captured longitude, device/source, geofence validation status, distance, evidence attachment.
- Add `Attendance Validation Log` for auditability.
- Add `Attendance Correction Request` if standard `Attendance Request` is insufficient.
- Add mobile/API endpoint wrapper after server validation is stable.
- Delay face/liveness to P3; store evidence/status fields now.

Priority:
- P0 for GPS/geofence/correction.
- P3 for face/liveness.

### 7. Shift Management

ERPNext/HRMS coverage:
- `Shift Type`
- `Shift Assignment`
- `Shift Request`
- `Shift Schedule`

Gap:
- rotating/overnight rule testing and user-facing schedule UX need care.
- shift-change approvals need workflow polish.

Recommended implementation:
- Use standard shift DocTypes.
- Add workflow and reports.
- Add overnight and late/early edge-case smoke tests.

Priority:
- P0.

### 8. Leave / Time-Off Management

ERPNext/HRMS coverage:
- `Leave Type`
- `Leave Policy`
- `Leave Allocation`
- `Leave Application`
- `Leave Ledger Entry`
- approval workflows.

Gap:
- mobile UX, leave calendar, policy templates, branch-specific rules may need custom reports/config.

Recommended implementation:
- Use standard leave engine.
- Configure workflow and roles.
- Add manager leave calendar report.
- Add leave balance card in ESS.

Priority:
- P0.

### 9. Overtime Management

ERPNext/HRMS coverage:
- `Overtime Slip`
- `Overtime Type`
- overtime salary components in HRMS.

Gap:
- overtime plan-before-work flow may need custom DocType/workflow.
- Indonesian overtime rule configuration may need custom logic.
- source traceability to payroll needs custom layer.

Recommended implementation:
- Use standard `Overtime Slip` where possible.
- Add `Overtime Request` only if planning workflow cannot fit standard model.
- Link approved overtime to payroll source trace.

Priority:
- P0/P1.

### 10. Timesheet

ERPNext coverage:
- `Timesheet` exists.

Gap:
- HR attendance and project timesheet concepts differ.
- PRD wants work-hour compliance, not only billable time.

Recommended implementation:
- Do not force all attendance into Timesheet unless needed.
- Build attendance compliance report from `Attendance`, `Employee Checkin`, `Shift Assignment`, and overtime records.

Priority:
- P1.

### 11. Payroll Management

ERPNext/HRMS coverage:
- `Salary Component`
- `Salary Structure`
- `Salary Slip`
- `Payroll Entry`
- `Payroll Period`
- `Additional Salary`
- payroll approval/submission workflow.

Gap:
- Indonesian PPh 21, BPJS, THR, e-Bupot/Coretax are not complete product-ready features without localization.
- payroll preview warnings/blocking issues need custom quality gates.
- attendance/leave/overtime/reimbursement source traceability needs custom layer.

Current/custom foundation expected:
- payroll source traceability in custom app.
- salary slip summary fields.

Recommended implementation:
- Keep official payroll DocTypes.
- Add Indonesia Payroll Settings, Tax Profile, BPJS Profile, THR rules.
- Add `Payroll Source Trace` for each payroll run/slip.
- Add validation report before submit.
- Add export formats for payroll, tax, BPJS.

Priority:
- P0/P1.

### 12. Reimbursement and Expense

ERPNext coverage:
- `Expense Claim`
- `Expense Claim Type`
- `Employee Advance`
- attachments and approval.

Gap:
- reimbursement limit/balance, receipt duplicate warning, Talenta-like mobile UX.

Recommended implementation:
- Use `Expense Claim` as base.
- Add reimbursement policy/balance only if required.
- Add duplicate receipt warning later using file hash/vendor/date/amount heuristic.
- Link approved claims into payroll source trace if paid through payroll.

Priority:
- P0/P1.

### 13. HR Document Management

ERPNext/Frappe coverage:
- file attachments.
- print formats.
- document generation through templates possible.

Gap:
- HR letter request, HR letter templates, automatic numbering, e-signature integration are not complete as product module.

Current/custom foundation expected:
- `HR Document Request`
- `HR Letter Template`

Recommended implementation:
- Use custom DocTypes for HR document request/template lifecycle.
- Use Print Format/Jinja templates for generated letters.
- Add e-signature integration later.

Priority:
- P1.

### 14. Asset Management

ERPNext coverage:
- ERPNext has Asset module for fixed assets.

Gap:
- employee asset assignment lifecycle and offboarding return checklist may need HR-specific wrapper.

Current/custom foundation expected:
- asset assignment foundation.

Recommended implementation:
- Link ERPNext `Asset` to employee assignment records.
- Add return condition, assigned date, returned date, offboarding task linkage.

Priority:
- P1.

### 15. Onboarding and Offboarding

HRMS coverage:
- `Employee Onboarding`
- `Employee Separation`
- `Exit Interview`
- `Full and Final Statement`

Gap:
- multi-department checklist UX and access removal tracking need polish.
- asset return and final payroll integration need custom links.

Recommended implementation:
- Use standard onboarding/separation DocTypes.
- Extend with checklist templates and linked tasks if needed.
- Add offboarding completion hook to update employee status after checks.

Priority:
- P1.

### 16. Recruitment / ATS

HRMS coverage:
- `Staffing Plan`
- `Job Requisition`
- `Job Opening`
- `Job Applicant`
- `Interview`
- `Job Offer`

Gap:
- polished recruitment pipeline board, candidate portal, assessment test, AI scoring are not complete.

Recommended implementation:
- Use standard recruitment DocTypes.
- Add pipeline dashboard and candidate stage reports.
- Delay AI scoring to P3.

Priority:
- P1.

### 17. Performance Management

HRMS coverage:
- `Appraisal`
- `Appraisal Cycle`
- `Goal`
- `KRA`
- `Employee Skill Map`
- skill assessment/training basics.

Gap:
- OKR experience, 360 review, review summary, analytics need extension.

Recommended implementation:
- Use standard appraisal/goals first.
- Add KPI/OKR fields or reports only after performance process is defined.
- Delay AI review summary until real review data exists.

Priority:
- P1/P2.

### 18. Talent Management and LMS

HRMS coverage:
- skill map/training basics.

Gap:
- full LMS, IDP, succession, talent pool are advanced and not Talenta-equivalent out of box.

Recommended implementation:
- Start with competency and training records.
- Integrate external LMS later if product requires full learning content delivery.
- Delay succession planning.

Priority:
- P2.

### 19. Analytics and Dashboard

ERPNext/Frappe coverage:
- reports, query reports, dashboard charts, workspaces.

Gap:
- ready-made HR executive dashboards and pivot-style exploration need custom work.

Recommended implementation:
- Build query reports and dashboard charts:
  - Headcount Dashboard
  - Attendance Dashboard
  - Payroll Cost Dashboard
  - Overtime Dashboard
  - Turnover Dashboard
  - Recruitment Dashboard
  - Performance Dashboard
- Keep SQL/report code in custom app.

Priority:
- P0 for basic dashboards, P2 for pivot/custom builder.

### 20. AI HR Assistant

ERPNext/HRMS coverage:
- none native.

Gap:
- permission-safe natural language data access must be designed carefully.

Recommended implementation:
- Build only after RBAC, reports, and clean data are stable.
- AI must query approved report/API layer, not raw unrestricted database.
- Log prompts, user, source reports, returned record references, and permission checks.
- Label predictions as predictions.

Priority:
- P3.

### 21. Integration and Open API

Frappe coverage:
- REST API for DocTypes.
- token auth/API keys.
- hooks and background jobs.
- webhook features can be configured/extended.

Gap:
- public product API needs stable contracts, docs, auth policy, rate limiting, and event naming.
- accounting/ERP/e-signature/LMS/bank/tax integrations need adapters.

Recommended implementation:
- Do not expose raw DocType API as final public API for all cases.
- Add versioned API wrappers for employee, attendance, leave, overtime, payroll, payslip, reimbursement.
- Add webhook event log and retry queue.
- Add integration log DocType.

Priority:
- P1/P2.

### 22. Security, Roles, Audit

ERPNext/Frappe coverage:
- RBAC.
- user permissions.
- document versions.
- audit/logs.
- session controls.

Gap:
- encryption-at-rest for specific fields, MFA policy, rate limiting, AI access audit, and branch/reporting-line scoping need product decisions.

Recommended implementation:
- Use Frappe roles and user permissions first.
- Add custom permission query conditions where manager/team scoping is required.
- Add audit logs for attendance validation, payroll source trace, payroll unlock/revision, AI answers.
- Avoid storing secrets in custom DocTypes unless encrypted/password field type is used.

Priority:
- P0.

## PRD MVP fit against ERPNext HRMS

### PRD Phase 1: Core HR + Attendance + ESS

Fit:
- Good foundation but needs custom attendance validation and ESS/MSS UX.

Use standard:
- Employee, Company, Department, Designation, Branch.
- Employee Checkin, Attendance, Shift Type, Shift Assignment.
- Leave Application, Leave Allocation, Leave Policy.
- Workflow, Role Permission Manager.

Build custom:
- geofence/location/policy validation.
- attendance correction and validation audit.
- ESS request center.
- manager approval dashboard.
- basic HR overview/attendance dashboard.

### PRD Phase 2: Payroll + Reimbursement

Fit:
- Good generic payroll engine, but Indonesia payroll localization is main work.

Use standard:
- Salary Structure, Salary Component, Payroll Entry, Salary Slip, Additional Salary.
- Expense Claim.

Build custom:
- BPJS profile/settings.
- PPh 21 settings/calculation support.
- THR rule.
- Payroll Source Trace.
- payroll validation warnings.
- reimbursement policy if needed.

### PRD Phase 3: Talent + Analytics + Integration

Fit:
- HRMS has basic recruitment and performance.
- Analytics/integration productization still custom.

Use standard:
- Staffing Plan, Job Requisition, Job Opening, Job Applicant, Interview, Job Offer.
- Appraisal, Appraisal Cycle, Goal, KRA.

Build custom:
- dashboards.
- API wrappers.
- webhook event log/retry.
- integration logs.

### PRD Phase 4: AI + Enterprise

Fit:
- Mostly custom.

Build later:
- AI HR assistant.
- AI performance summary.
- candidate scoring.
- resignation prediction.
- advanced analytics.

## Custom DocType candidate list

Already recommended or likely needed:
- Attendance Policy
- Geofence Location
- Attendance Validation Rule
- Attendance Validation Log
- Attendance Correction Request
- Attendance Device
- Attendance Sync Log
- External Attendance Import
- Payroll Source Trace
- Indonesia Payroll Settings
- Tax Profile Indonesia
- BPJS Profile
- THR Rule
- Payslip Publish Log
- HR Request
- Employee Data Change Request
- HR Document Request
- HR Letter Template
- HR Helpdesk Ticket
- Announcement
- Employee Asset Assignment
- Integration Event Log
- Webhook Delivery Log
- AI Query Audit Log

Rule:
- Create custom DocType only when official HRMS DocType cannot represent the concept cleanly.

## Recommended implementation sequence

### Sprint A: Benchmark cleanup and acceptance baseline

Deliverables:
- Current-state audit update.
- This benchmark doc.
- Gap map aligned to PRD IDs.
- Smoke test list for current HRMS extensions.

No schema changes.

### Sprint B: ESS/MSS minimum product

Deliverables:
- Employee request center.
- Manager approval dashboard.
- Team attendance report.
- Team leave calendar.
- Role/permission smoke tests.

### Sprint C: Attendance hardening

Deliverables:
- Geofence validation complete.
- Correction request workflow.
- Late/early/missing checkout report.
- Overnight shift tests.
- Attendance-to-payroll input trace.

### Sprint D: Payroll Indonesia foundation

Deliverables:
- BPJS profile/settings.
- PPh 21 configuration skeleton.
- THR rule skeleton.
- payroll blocking warnings.
- payslip source trace visible to payroll admin.

### Sprint E: HR Admin automation

Deliverables:
- HR document request/template.
- asset assignment/offboarding links.
- announcement.
- HR helpdesk.

### Sprint F: Analytics and integration

Deliverables:
- Headcount dashboard.
- Attendance dashboard.
- Payroll cost dashboard.
- API wrapper docs.
- webhook event log/retry.

### Sprint G: AI guarded prototype

Prerequisite:
- stable RBAC and reports.

Deliverables:
- AI query over approved report layer only.
- permission checks.
- audit log.
- source citation.

## Key risks

Payroll accuracy:
- Highest risk.
- Mitigation: source trace, preview, blocking warnings, approval, rollback/revision audit, regression fixtures.

Attendance fraud:
- High risk.
- Mitigation: GPS/geofence first, evidence attachment, liveness provider later, validation log.

Permission leakage:
- High risk.
- Mitigation: role matrix tests, report-level filters, AI permission gate.

Core drift:
- Medium/high risk.
- Mitigation: no core edits, app fixtures, migrations, hooks, reports in custom app.

Complexity creep:
- High risk.
- Mitigation: phase AI/LMS/succession later. Build daily HR flows first.

## Acceptance baseline for current benchmark

Benchmark is complete when:
- Each PRD major module has ERPNext/HRMS coverage assessment.
- Each gap has standard-vs-custom recommendation.
- MVP sequence is clear.
- No recommendation requires editing ERPNext/Frappe/HRMS core.
- Indonesia payroll is explicitly treated as custom/localization work.
- AI is deferred until permission-safe data/report layer exists.

## Operating rules for implementation

- Read existing DocTypes and fields before adding custom fields.
- Prefer official HRMS DocTypes.
- Use fixtures for Custom Field, DocType, Workflow, Role, Report, Workspace, Dashboard Chart.
- Smoke test setup functions with rollback before exporting fixtures.
- Copy exported fixtures from container back to host repo before commit.
- Verify `git status --short --branch` before reporting done.
- Push only after explicit approval.
