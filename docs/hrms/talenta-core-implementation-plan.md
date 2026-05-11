# HRMS Talenta-Core Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build or update ERPNext HRMS using Mekari Talenta feature report as main product rulebook while keeping ERPNext/Frappe core untouched.

**Architecture:** Use official ERPNext + HRMS as base. Put all custom DocTypes, fields, workflows, reports, permissions, hooks, fixtures, and integrations in `oakglobal_erp_custom`. Prefer extending existing HRMS DocTypes before creating new DocTypes.

**Tech Stack:** ERPNext/Frappe v16, HRMS app, MariaDB, Redis, Docker, custom Frappe app `oakglobal_erp_custom`, Frappe fixtures, Frappe Query Reports, Dashboard Charts, REST API/Webhooks.

---

## 1. Product Rules

Talenta report becomes coverage checklist, not source-code blueprint.

Rules:
- Keep ERPNext/Frappe/HRMS core untouched.
- Use standard HRMS DocTypes when they fit.
- Add custom fields when standard DocType is enough.
- Create custom DocTypes only for missing domain concepts.
- Export all UI/config changes as fixtures.
- All payroll/tax/BPJS logic must be configurable and auditable.
- AI features must wait until clean HR data exists.
- No DocType/file names need `Oak` prefix unless business identity specifically requires it.

Naming style:
- Clean names: `Attendance Policy`, `Geofence Location`, `Payroll Audit Log`.
- Avoid noisy names: `Oak Attendance Policy`, `Oak Payroll Audit Log`.
- Python modules can stay under `oakglobal_erp_custom` because app name is fixed.

---

## 2. Feature Groups From Talenta Report

Required coverage groups:
1. Attendance and time management
2. Payroll, compensation, benefits
3. HR administration / HRIS
4. Employee self-service / mobile-like workflows
5. Talent acquisition
6. Talent development
7. AI and analytics
8. Integrations and platform
9. Security, access, audit, support
10. Public utility calculators/templates where useful

---

## 3. Priority Model

P0 — MVP required:
- Employee profile extension
- Attendance, shift, leave, overtime
- ESS request flows
- Payroll input/audit foundation
- Reimbursement
- Basic dashboards
- RBAC/security

P1 — strong HRMS:
- Recruitment/manpower planning
- Performance/KPI/OKR
- Competency and IDP
- Onboarding/offboarding improvements
- Device/API integrations

P2 — advanced:
- LMS
- Succession planning
- Pivot-style analytics
- Payroll disbursement batches
- e-Bupot/Coretax preparation

P3 — AI:
- HR chatbot
- candidate scoring
- review summaries
- resignation risk
- attendance fraud/anomaly detection

---

## 4. Target Repository Layout

Create docs first:

```text
docs/hrms/
  talenta-core-implementation-plan.md
  talenta-feature-gap-map.md
  security-and-permissions.md
  payroll-indonesia-rules.md
  workflows.md
  test-plan.md
```

Future code layout:

```text
oakglobal_erp_custom/hrms_ext/
  attendance/
  payroll/
  employee_admin/
  recruitment/
  performance/
  learning/
  analytics/
  integrations/
  security/
```

Fixtures:

```text
oakglobal_erp_custom/fixtures/
  custom_field.json
  role.json
  workflow.json
  workflow_state.json
  workflow_action_master.json
  workspace.json
  property_setter.json
  report.json
  dashboard_chart.json
  number_card.json
```

---

## 5. Existing HRMS First Mapping

Before creating custom DocTypes, inspect existing DocTypes:

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec backend \
  bench --site erp.localhost list-apps

docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec backend \
  bench --site erp.localhost execute frappe.get_all \
  --kwargs '{"doctype":"DocType","filters":{"module":["in",["HR","Payroll","Recruitment"]]},"pluck":"name"}'
```

Expected installed apps:
- `frappe`
- `erpnext`
- `hrms`
- `oakglobal_erp_custom`

Decision rules:
- If HRMS already owns core transaction, extend it.
- If workflow missing, add Workflow fixture.
- If reporting missing, add Query Report.
- If compliance/audit missing, add custom DocType.

---

## 6. MVP Module Plan

### 6.1 Employee Profile Extension

Base DocType:
- `Employee`

Add fields only if missing:
- employee category
- work location
- branch/geofence location
- tax status
- BPJS number
- bank account metadata reference
- emergency contact structured fields
- onboarding status
- offboarding status
- asset summary

Acceptance:
- HR can maintain complete employee data.
- Employee profile becomes source of truth for attendance/payroll/recruitment/performance.
- Sensitive payroll/tax fields restricted by role.

---

### 6.2 Attendance and Time Management

Base HRMS DocTypes:
- `Employee Checkin`
- `Attendance`
- `Shift Type`
- `Shift Assignment`
- `Leave Application`
- `Attendance Request`

Custom DocTypes if missing:
- `Geofence Location`
- `Attendance Policy`
- `Attendance Validation Log`
- `Live Attendance Event`
- `Attendance Device`
- `Attendance Sync Log`

Talenta rules covered:
- online attendance
- GPS/geofencing
- face/selfie evidence field
- liveness validation status placeholder
- live attendance tracking
- shift management
- leave sync
- overtime sync
- fingerprint/device import support
- attendance-to-payroll sync

MVP behavior:
- Check-in stores latitude, longitude, source, device, selfie/evidence attachment.
- Geofence validation sets status: `Valid`, `Outside Geofence`, `Missing Location`, `Manual Review`.
- Invalid attendance requires approval before payroll inclusion.
- Attendance summary feeds payroll period.

---

### 6.3 Leave, Shift Change, Overtime

Base HRMS:
- `Leave Application`
- `Shift Assignment`
- `Attendance Request`

Custom DocTypes:
- `Overtime Request`
- `Shift Change Request`
- `Attendance Correction Request`

Workflow states:
- Draft
- Submitted
- Manager Approved
- HR Approved
- Rejected
- Cancelled

Rules:
- Approved leave updates attendance.
- Approved shift change updates schedule.
- Approved overtime becomes payroll input.
- Overtime before approval marked exception.

---

### 6.4 Payroll, Compensation, Benefits

Base HRMS:
- `Salary Structure`
- `Salary Slip`
- `Payroll Entry`
- `Additional Salary`

Custom DocTypes:
- `Payroll Period Rule`
- `Payroll Component Mapping`
- `BPJS Setting`
- `PPh21 Setting`
- `Payroll Audit Log`
- `Payroll Input Summary`
- `Payslip Publish Log`
- `Payroll Disbursement Batch`

Talenta rules covered:
- payroll calculation foundation
- PPh21 config
- BPJS/JHT config
- payroll reporting
- payroll cut-off
- digital payslip tracking
- audit/reporting
- reimbursement/overtime sync
- future Coretax/e-Bupot integration

Risk:
- Indonesian payroll/tax must be validated by accountant before production use.

Rules:
- Every salary slip can trace source attendance/overtime/leave/reimbursement.
- Manual override requires reason.
- Payroll run creates audit log.
- Tax/BPJS rates configurable by effective date.

---

### 6.5 Reimbursement and Expense

Base option:
- Use `Expense Claim` if installed and suitable.

Custom DocTypes if needed:
- `Reimbursement Policy`
- `Reimbursement Balance`
- `Reimbursement Request`
- `Reimbursement Disbursement Log`

Rules:
- Attachment required.
- Category limits configurable.
- Over-limit claim needs higher approval.
- Approved reimbursement syncs to payroll or payment batch.

---

### 6.6 HR Administration / ESS

Base HRMS/Frappe:
- `Employee Onboarding`
- `Employee Separation`
- `ToDo`
- `Assignment Rule`

Custom DocTypes:
- `HR Request`
- `Employee Data Change Request`
- `HR Document Request`
- `HR Letter Template`
- `Asset Assignment`
- `Helpdesk Ticket`
- `Announcement`

Talenta rules covered:
- ESS
- digital forms and approvals
- HR documents
- asset management
- onboarding/offboarding
- helpdesk
- internal announcements
- request management

Rules:
- Employee cannot directly edit sensitive profile data.
- Change request updates Employee only after approval.
- Offboarding cannot complete until assigned assets returned.

---

## 7. P1 Module Plan

### 7.1 Talent Acquisition

Base HRMS:
- `Job Opening`
- `Job Applicant`
- `Interview`
- `Job Offer`

Custom DocTypes:
- `Manpower Plan`
- `Candidate Scorecard`
- `Recruitment Pipeline Rule`
- `Applicant Assessment`
- `Recruitment AI Score`

Rules:
- Job Opening should link to approved Manpower Plan.
- Candidate scoring supports HR decision, does not replace it.
- Accepted candidate starts onboarding without duplicate data entry.

---

### 7.2 Talent Development

Base HRMS:
- `Appraisal`
- `Goal`

Custom DocTypes:
- `KPI Template`
- `OKR Cycle`
- `360 Review`
- `Competency Map`
- `Individual Development Plan`
- `Succession Plan`
- `Learning Course`
- `Learning Enrollment`
- `Certificate`

Rules:
- Review cycle links to KPI/OKR.
- IDP generated from competency gaps.
- Succession planning restricted to HR leadership roles.

---

## 8. Analytics Plan

Reports/dashboards:
- `Headcount Dashboard`
- `Attendance Dashboard`
- `Payroll Cost Dashboard`
- `Overtime Dashboard`
- `Turnover Dashboard`
- `Performance Dashboard`
- `Recruitment Dashboard`

Metrics:
- headcount by branch/division/title/tenure
- attendance rate
- lateness
- absence
- leave usage
- overtime hours/cost
- payroll cost by component
- turnover/resignation
- recruitment funnel
- performance score distribution

Permissions:
- Employee sees own data.
- Manager sees reporting line.
- HR sees company-wide HR data.
- Payroll sees payroll data.
- Admin sees config/audit.

---

## 9. Integration Plan

Custom DocTypes:
- `Webhook Endpoint`
- `Integration Log`
- `External Attendance Import`
- `Device Integration Setting`
- `Payroll Journal Mapping`

Integration targets:
- attendance devices/fingerprint/Hikvision-like import
- accounting journal sync
- REST API for internal apps
- webhooks for employee/attendance/payroll events
- future WhatsApp/Telegram/Hermes ESS agent

Rules:
- All inbound/outbound payloads logged with status.
- Secrets stored in site config or Password fields, never committed.
- Failed sync retryable.

---

## 10. AI Plan

Do after P0/P1 data quality is stable.

Features:
- HR chatbot
- performance review summary
- resignation risk
- candidate scoring
- attendance anomaly detection

Rules:
- AI obeys ERPNext permissions.
- AI output is recommendation only.
- Payroll answers restricted.
- Every AI query logged.
- No raw secrets or private documents sent to external model without approval.

---

## 11. Security and Access

Roles:
- HR User
- HR Manager
- Payroll User
- Payroll Manager
- Department Manager
- Employee Self Service
- Recruiter
- Performance Reviewer
- HR Admin

Security requirements:
- RBAC per DocType
- field-level protection for tax/payroll fields
- audit logs for payroll and employee data changes
- approval workflow for sensitive updates
- API keys separated by integration
- no secrets in fixtures/repo

---

## 12. Implementation Sprints

### Sprint 1 — Audit and Gap Map
- Inspect installed apps and HRMS DocTypes.
- Create `talenta-feature-gap-map.md`.
- Confirm MVP scope.
- No schema changes.

### Sprint 2 — Employee and ESS Foundation
- Add Employee custom fields.
- Add HR roles.
- Add `HR Request` and `Employee Data Change Request`.
- Add workflows and permissions.
- Export fixtures.

### Sprint 3 — Attendance MVP
- Add geofence/policy/log DocTypes.
- Extend Employee Checkin/Attendance.
- Add validation logic.
- Add attendance exception workflow.

### Sprint 4 — Leave, Shift, Overtime
- Add Overtime Request.
- Add Shift Change Request.
- Add Attendance Correction Request.
- Add payroll inclusion flags.

### Sprint 5 — Payroll Foundation
- Add payroll config DocTypes.
- Add payroll input summary.
- Add payroll audit log.
- Add payslip publish log.

### Sprint 6 — Reimbursement
- Decide Expense Claim extension vs custom request.
- Add reimbursement policy/balance/request.
- Add approval/disbursement workflow.

### Sprint 7 — HR Admin
- Add HR document request/template.
- Add asset assignment.
- Add helpdesk ticket.
- Add announcements.
- Improve onboarding/offboarding checklist.

### Sprint 8 — Recruitment
- Add manpower plan.
- Add scorecard/assessment.
- Link applicant to onboarding.

### Sprint 9 — Performance
- Add KPI/OKR cycle.
- Add 360 review.
- Add competency map and IDP.

### Sprint 10 — Analytics and Integration
- Add dashboards/reports.
- Add integration logs/webhook settings.
- Prepare AI-safe query layer design.

---

## 13. Acceptance Criteria

MVP complete when:
- Employee profile supports required HR/payroll fields.
- Employee can submit leave, overtime, shift change, attendance correction, reimbursement, HR request.
- Manager/HR approvals work.
- Attendance exceptions are auditable.
- Attendance/overtime/reimbursement can feed payroll input summary.
- Payroll run has audit trail.
- Payslip publish tracked.
- Basic headcount, attendance, payroll dashboards exist.
- Roles restrict sensitive data.
- Fixtures export cleanly.
- ERPNext/Frappe/HRMS core untouched.

---

## 14. Verification Commands

Run after each implementation sprint:

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec backend \
  bench --site erp.localhost migrate

docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec backend \
  bench --site erp.localhost clear-cache

docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec backend \
  bench --site erp.localhost export-fixtures

docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec backend \
  bench --site erp.localhost list-apps
```

Repo checks:

```bash
git status --short
git diff --check
git add docs/hrms oakglobal_erp_custom
git commit -m "docs: add Talenta-core HRMS implementation plan"
git push origin dev
```
