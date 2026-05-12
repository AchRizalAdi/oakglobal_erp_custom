# Sprint 11 — ESS/MSS Foundation

Status: planned
Target stack: ERPNext/Frappe v16 + HRMS v16 + `oakglobal_erp_custom`
Site: `erp.localhost`
Branch: `dev`

## Goal

Close the biggest daily-use gap from the Talenta-inspired PRD: Employee Self-Service (ESS) and Manager Self-Service (MSS).

This sprint should make employees able to submit and track common HR requests, and managers able to see team data and approvals without HR Admin access.

## Current state snapshot

Apps installed:
- frappe 16.17.5
- erpnext 16.17.0
- hrms 16.6.1
- oakglobal_erp_custom 0.0.1

Existing custom DocTypes relevant to this sprint:
- `HR Request`
- `Employee Data Change Request`
- `Employee Data Change Request Field`
- `Attendance Correction Request`
- `Shift Change Request`
- `Announcement`
- `Helpdesk Ticket`
- `HR Document Request`
- `Asset Assignment`

Existing workflows:
- `HR Request Workflow`
- `Employee Data Change Request Workflow`

Implication:
- Do not create duplicate request DocTypes unless needed.
- Sprint should mostly add reports, workspace/dashboard fixtures, permissions, and smoke tests around existing DocTypes.

## Scope

### P0 deliverables

1. Employee Request Center
   - Employee can see own open requests across:
     - HR Request
     - Employee Data Change Request
     - Attendance Correction Request
     - Shift Change Request
     - Leave Application
     - Expense Claim
     - HR Document Request
     - Helpdesk Ticket
   - Employee can see status, request type, created date, approver/current state, and link to source document.

2. Manager Approval Dashboard
   - Manager can see pending approvals for team/request documents.
   - Include HR Request and Employee Data Change Request first.
   - Add Leave Application, Expense Claim, Attendance Correction Request, Shift Change Request if permission model supports it.

3. Team Attendance Report
   - Manager sees team attendance summary by date range.
   - HR sees all.
   - Employee sees only self.
   - Fields: employee, date, shift, status, in time, out time, late, early exit, source/validation status if available.

4. Team Leave Calendar Report
   - Manager sees approved/pending leave for team.
   - HR sees all.
   - Employee sees self.
   - Fields: employee, leave type, from date, to date, status, workflow state.

5. Pending Approval Report
   - Combined list of approval items relevant to current user.
   - Start with Workflow Action if available, then add domain-specific query if needed.

6. Permission smoke tests
   - Employee can access own records only.
   - Manager can access direct reports.
   - HR Admin can access all.
   - Payroll Admin does not get broad HR write access by accident.

### P1 deliverables

1. ESS Workspace
   - Shortcuts/cards for request center, leave, attendance, expense, payslip, announcements, HR documents.

2. Manager Workspace
   - Shortcuts/cards for approvals, team attendance, team leave calendar, overtime, reimbursement, team profile list.

3. Notification polish
   - Pending approval notification.
   - Request approved/rejected notification.

## Out of scope

- Native mobile app.
- Face recognition/liveness.
- AI HR assistant.
- Payroll Indonesia calculation changes.
- LMS/talent/succession.
- Core edits to ERPNext/Frappe/HRMS.

## Recommended implementation approach

Prefer Frappe Query Reports and Workspaces first. Avoid new DocTypes unless current data model cannot support the report.

Expected files:

```text
oakglobal_erp_custom/hrms_ext/setup_ess_mss.py
oakglobal_erp_custom/report/employee_request_center/employee_request_center.py
oakglobal_erp_custom/report/employee_request_center/employee_request_center.json
oakglobal_erp_custom/report/manager_approval_dashboard/manager_approval_dashboard.py
oakglobal_erp_custom/report/manager_approval_dashboard/manager_approval_dashboard.json
oakglobal_erp_custom/report/team_attendance_summary/team_attendance_summary.py
oakglobal_erp_custom/report/team_attendance_summary/team_attendance_summary.json
oakglobal_erp_custom/report/team_leave_calendar/team_leave_calendar.py
oakglobal_erp_custom/report/team_leave_calendar/team_leave_calendar.json
oakglobal_erp_custom/report/pending_approval_items/pending_approval_items.py
oakglobal_erp_custom/report/pending_approval_items/pending_approval_items.json
```

Hook/fixture updates:

```python
fixtures = [
    {"doctype": "Report", "filters": [["name", "in", [
        "Employee Request Center",
        "Manager Approval Dashboard",
        "Team Attendance Summary",
        "Team Leave Calendar",
        "Pending Approval Items",
    ]]]},
    {"doctype": "Workspace", "filters": [["name", "in", [
        "Employee Self Service",
        "Manager Self Service",
    ]]]},
]
```

Merge with existing fixture filters. Do not replace unrelated filters.

## Permission model

### Employee

Allowed:
- own Employee-linked request records.
- own attendance/leave/expense/payslip records.
- announcements marked visible to employees.

Denied:
- other employee payroll/profile data.
- team dashboards.

### Manager

Allowed:
- direct reports by `Employee.reports_to`.
- pending approvals assigned through workflow.
- team attendance/leave/overtime summary.

Denied:
- payroll details unless explicitly granted.
- employees outside reporting tree.

### HR Admin / HR Manager

Allowed:
- all HR operational records.

### Payroll Admin

Allowed:
- payroll-related views.
- no broad write access to HR admin records unless assigned.

## Report behavior

### Employee Request Center

Sources:
- `tabHR Request`
- `tabEmployee Data Change Request`
- `tabAttendance Correction Request`
- `tabShift Change Request`
- `tabLeave Application`
- `tabExpense Claim`
- `tabHR Document Request`
- `tabHelpdesk Ticket`

Normalize columns:
- source_doctype
- source_name
- request_type
- subject
- employee
- employee_name
- status
- workflow_state
- creation
- modified
- owner

### Manager Approval Dashboard

Sources:
- Prefer `Workflow Action` if reliable.
- Supplement with request DocTypes where manager is explicit approver or employee reports to current user's employee record.

Columns:
- source_doctype
- source_name
- request_type
- employee
- employee_name
- status
- workflow_state
- age_hours
- pending_with
- link

### Team Attendance Summary

Sources:
- `Attendance`
- `Employee Checkin`
- `Shift Assignment`
- custom validation fields/logs where available.

Columns:
- attendance_date
- employee
- employee_name
- department
- shift
- status
- in_time
- out_time
- late_entry
- early_exit
- validation_status

### Team Leave Calendar

Sources:
- `Leave Application`

Columns:
- employee
- employee_name
- leave_type
- from_date
- to_date
- total_leave_days
- status
- workflow_state

### Pending Approval Items

Sources:
- `Workflow Action`
- fallback: domain query by workflow_state/status.

Columns:
- reference_doctype
- reference_name
- subject
- status
- workflow_state
- assigned_to
- created_age

## Smoke test plan

Setup module should include `smoke_test()` with rollback where possible.

Checks:
- Reports exist.
- Report JSON is valid.
- Query functions return columns and list result.
- Employee user context does not return other employee records.
- Manager user context returns only direct-report records.
- HR user context can return all sample records.
- Payroll role is not included in HR write permissions accidentally.

If full user fixture data is not available, smoke test should at least validate report registration, permission helper functions, and SQL compiles with safe filters.

## Implementation commands

Copy changed code into backend before testing because local repo is not automatically mounted into the image-baked app:

```bash
cd ~/oak_erp
docker cp oakglobal_erp_custom/oakglobal_erp_custom/hooks.py \
  oaklocal-backend-1:/home/frappe/frappe-bench/apps/oakglobal_erp_custom/oakglobal_erp_custom/hooks.py
docker cp oakglobal_erp_custom/oakglobal_erp_custom/hrms_ext/setup_ess_mss.py \
  oaklocal-backend-1:/home/frappe/frappe-bench/apps/oakglobal_erp_custom/oakglobal_erp_custom/hrms_ext/setup_ess_mss.py
```

Run smoke/setup/export:

```bash
docker compose --project-name oaklocal -f local/compose.yaml exec -T backend \
  bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_ess_mss.smoke_test

docker compose --project-name oaklocal -f local/compose.yaml exec -T backend \
  bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_ess_mss.run

docker compose --project-name oaklocal -f local/compose.yaml exec -T backend \
  bench --site erp.localhost export-fixtures
```

Copy fixtures back:

```bash
cd ~/oak_erp
mkdir -p oakglobal_erp_custom/oakglobal_erp_custom/fixtures
docker cp oaklocal-backend-1:/home/frappe/frappe-bench/apps/oakglobal_erp_custom/oakglobal_erp_custom/fixtures/. \
  oakglobal_erp_custom/oakglobal_erp_custom/fixtures/
```

Validate:

```bash
cd ~/oak_erp/oakglobal_erp_custom
python3 -m py_compile oakglobal_erp_custom/hooks.py oakglobal_erp_custom/hrms_ext/setup_ess_mss.py
python3 -m json.tool oakglobal_erp_custom/fixtures/report.json >/dev/null
python3 -m json.tool oakglobal_erp_custom/fixtures/workspace.json >/dev/null
git diff --check
```

Commit:

```bash
git add docs/hrms oakglobal_erp_custom
git commit -m "feat: add ESS MSS foundation"
GIT_SSH_COMMAND="ssh -i $HOME/.ssh/hermes_wsl_github_ed25519 -o IdentitiesOnly=yes" git push origin dev
```

## Acceptance criteria

Done when:
- Sprint doc exists and is committed.
- Reports exist as fixtures and files.
- Employee request center returns own request data.
- Manager dashboard can show direct-report requests/approvals.
- Team attendance and leave reports are scoped safely.
- Permission helper tests pass.
- No ERPNext/Frappe/HRMS core files changed.
- Commit is pushed to `dev`.

## Risks

Permission leakage:
- Highest risk.
- Use conservative default: if user has no HR role and no linked Employee, return empty result.

Report performance:
- Use date filters and limit defaults.
- Avoid unrestricted full-table scans.

Workflow variation:
- `Workflow Action` may not cover every custom request cleanly.
- Keep fallback domain queries per DocType.

Duplicate concepts:
- Avoid creating new generic request DocType if `HR Request` already covers it.

Payroll privacy:
- Do not include salary slips/payroll values in ESS/MSS reports except own payslip links.
