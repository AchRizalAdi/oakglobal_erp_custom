# Current HRMS State Audit

Date: 2026-05-11
Environment: WSL Ubuntu host `rijoll`, local Docker project `oaklocal`

## Summary

Local ERPNext stack is running and has official HRMS installed. Custom app is installed but currently almost empty from HRMS feature perspective. No custom HRMS DocTypes or Workflows exist yet. This is good: we can build cleanly in `oakglobal_erp_custom` without undoing prior custom HRMS work.

## Docker State

Project: `oaklocal`
Compose file: `~/oak_erp/local/compose.yaml`

Running services:
- `oaklocal-frontend-1` — up, port `8080:8080`
- `oaklocal-backend-1` — up
- `oaklocal-websocket-1` — up
- `oaklocal-scheduler-1` — up
- `oaklocal-queue-short-1` — up
- `oaklocal-queue-long-1` — up
- `oaklocal-redis-cache-1` — up
- `oaklocal-redis-queue-1` — up
- `oaklocal-db-1` — up, healthy

Detected site:
- `erp.localhost`

## Installed Apps

```text
frappe               16.17.5 UNVERSIONED
erpnext              16.17.0 UNVERSIONED
hrms                 16.6.1  UNVERSIONED
oakglobal_erp_custom 0.0.1   UNVERSIONED
```

Interpretation:
- ERPNext v16 and HRMS v16 are present.
- Custom app is installed.
- `UNVERSIONED` is normal for image-baked/container app installs without full git metadata.

## Custom App State

Repo path:
- `~/oak_erp/oakglobal_erp_custom`

Current useful files:
- `README.md`
- `docs/hrms/talenta-core-implementation-plan.md`
- `oakglobal_erp_custom/hooks.py`
- `oakglobal_erp_custom/config/desktop.py`
- `oakglobal_erp_custom/public/css/oakglobal_login.css`

No HRMS extension package exists yet:
- no `hrms_ext/`
- no fixtures directory
- no custom HRMS DocTypes
- no custom workflows

## Existing Custom Fields

Observed Custom Fields are from ERPNext/HRMS installation, not custom Talenta plan work.

Important Employee-related fields already available:
- `employment_type`
- `grade`
- `default_shift`
- `leave_approver`
- `expense_approver`
- `shift_request_approver`
- `payroll_cost_center`
- `employee_advance_account`
- `health_insurance_no`
- `health_insurance_provider`
- `job_applicant`

Department-related fields already available:
- `leave_approvers`
- `expense_approvers`
- `shift_request_approver`
- `payroll_cost_center`
- `leave_block_list`

Company-related payroll fields already available:
- `default_payroll_payable_account`
- `default_employee_advance_account`
- `default_expense_claim_payable_account`

## Existing Workflows

No active custom workflows found.

Implication:
- Approval behavior must be designed and added as Workflow fixtures.

## Existing Custom DocTypes

No custom DocTypes found.

Implication:
- New DocTypes can be introduced cleanly with no migration conflicts.

## HRMS Standard Coverage Found

Important existing HRMS DocTypes already cover large Talenta areas:

Attendance:
- `Attendance`
- `Attendance Request`
- `Employee Checkin`
- `Employee Attendance Tool`
- `Upload Attendance`
- `Shift Type`
- `Shift Assignment`
- `Shift Request`
- `Shift Location`
- `Shift Schedule`
- `Holiday List Assignment`

Leave:
- `Leave Application`
- `Leave Allocation`
- `Leave Policy`
- `Leave Type`
- `Leave Period`
- `Leave Ledger Entry`
- `Compensatory Leave Request`

Overtime:
- `Overtime Slip`
- `Overtime Type`
- `Overtime Details`
- `Overtime Salary Component`

Payroll:
- `Payroll Entry`
- `Payroll Period`
- `Payroll Settings`
- `Salary Structure`
- `Salary Structure Assignment`
- `Salary Slip`
- `Salary Component`
- `Additional Salary`
- `Income Tax Slab`
- `Payroll Correction`

Expense/Reimbursement:
- `Expense Claim`
- `Expense Claim Type`
- `Expense Claim Detail`
- `Employee Advance`

Recruitment:
- `Staffing Plan`
- `Job Requisition`
- `Job Opening`
- `Job Applicant`
- `Interview`
- `Interview Feedback`
- `Job Offer`
- `Appointment Letter`

Performance/Talent:
- `Appraisal`
- `Appraisal Cycle`
- `Appraisal Template`
- `Goal`
- `KRA`
- `Employee Skill`
- `Employee Skill Map`
- `Skill Assessment`
- `Training Program`
- `Training Event`
- `Training Result`

Onboarding/Offboarding:
- `Employee Onboarding`
- `Employee Onboarding Template`
- `Employee Separation`
- `Employee Separation Template`
- `Exit Interview`
- `Full and Final Statement`

## Main Gaps Before Build

Need custom/config work for:
- GPS/geofence attendance validation
- attendance selfie/liveness evidence and validation status
- live attendance event tracking
- Talenta-style ESS consolidated requests
- Indonesian payroll layer: BPJS/JHT/PPh21 effective-date settings and audit trail
- payroll source traceability from attendance/overtime/leave/reimbursement
- payslip publish log
- reimbursement policy/balance if standard Expense Claim not enough
- HR document request/templates with automatic numbering
- asset assignment lifecycle tied to offboarding
- HR helpdesk ticket if not using separate helpdesk app
- manpower planning enhancements if `Staffing Plan` not enough
- AI/candidate scoring/review summary later
- dashboard/report layer
- webhooks/integration logs

## Recommended Next Build Order

1. Create gap map from Talenta features to existing HRMS DocTypes.
2. Add fixtures config to `hooks.py`.
3. Build Employee/ESS foundation first.
4. Build Attendance geofence/evidence second.
5. Build payroll audit/input summary third.
6. Add dashboards after first real data flow works.

## Commands Used

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml ps
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend bench --site erp.localhost list-apps
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend bench version
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend bench --site erp.localhost execute frappe.get_all --kwargs '{...}'
```
