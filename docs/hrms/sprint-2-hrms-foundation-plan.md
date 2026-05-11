# Sprint 2 HRMS Foundation Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build first real HRMS foundation layer: fixtures setup, HR roles, Employee extension fields, generic HR Request, Employee Data Change Request, workflows, permissions, and verification/export flow.

**Architecture:** Use `oakglobal_erp_custom` only. Do not edit ERPNext/Frappe/HRMS core. Prefer Frappe fixtures for portability. Create clean DocType names without `Oak` prefix.

**Tech Stack:** ERPNext/Frappe v16, HRMS v16, custom app `oakglobal_erp_custom`, Frappe DocTypes, Custom Fields, Workflow, Role, fixtures.

---

## Preconditions

Local stack:

```text
project: oaklocal
compose: ~/oak_erp/local/compose.yaml
site: erp.localhost
custom repo: ~/oak_erp/oakglobal_erp_custom
```

Installed apps confirmed:

```text
frappe 16.17.5
erpnext 16.17.0
hrms 16.6.1
oakglobal_erp_custom 0.0.1
```

Current state:
- custom app installed
- no custom HRMS DocTypes yet
- no workflows yet
- `fixtures = []` in `hooks.py`

---

## Design Rules

- No core edits.
- No `Oak` prefix on DocType names.
- All DocTypes placed under existing app module `Oakglobal ERP Custom` unless a new clean module is added later.
- Every sensitive employee data change must go through approval.
- Employee Self Service users can create requests, not modify protected Employee fields directly.
- Managers approve first; HR final-approves.
- Export fixtures after every schema/workflow change.
- Commit after each small task.

---

## Deliverables

Files expected after Sprint 2:

```text
oakglobal_erp_custom/hooks.py
oakglobal_erp_custom/fixtures/custom_field.json
oakglobal_erp_custom/fixtures/role.json
oakglobal_erp_custom/fixtures/workflow.json
oakglobal_erp_custom/fixtures/workflow_state.json
oakglobal_erp_custom/fixtures/workflow_action_master.json
oakglobal_erp_custom/fixtures/custom_docperm.json
oakglobal_erp_custom/fixtures/doctype.json
docs/hrms/sprint-2-hrms-foundation-plan.md
```

DocTypes expected:
- `HR Request`
- `Employee Data Change Request`
- `Employee Data Change Request Field`

Roles expected:
- `HR Admin`
- `HR Manager`
- `Payroll Manager`
- `Payroll User`
- `Department Manager`
- `Employee Self Service`
- `Recruiter`
- `Performance Reviewer`

Employee custom fields expected:
- `branch_location`
- `work_location_type`
- `tax_status`
- `bpjs_kesehatan_no`
- `bpjs_ketenagakerjaan_no`
- `bank_account_name`
- `bank_account_no_masked`
- `emergency_contact_relation`
- `onboarding_status_detail`
- `offboarding_status_detail`

---

# Task 1: Create safety branch and verify clean state

**Objective:** Ensure work starts from clean `dev` branch.

**Files:** none

**Commands:**

```bash
cd ~/oak_erp/oakglobal_erp_custom
git checkout dev
git pull origin dev
git status --short
```

Expected:
- clean status
- branch `dev`

**Commit:** none

---

# Task 2: Add fixture configuration to hooks.py

**Objective:** Make future UI/schema changes exportable and portable.

**Modify:** `oakglobal_erp_custom/hooks.py`

Replace:

```python
# Fixtures can be added later to version-control UI customizations.
fixtures = []
```

With:

```python
# Version-controlled HRMS customizations.
# Keep filters tight enough to avoid exporting unrelated ERPNext/HRMS setup.
fixtures = [
    {
        "doctype": "Role",
        "filters": [["role_name", "in", [
            "HR Admin",
            "HR Manager",
            "Payroll Manager",
            "Payroll User",
            "Department Manager",
            "Employee Self Service",
            "Recruiter",
            "Performance Reviewer",
        ]]],
    },
    {
        "doctype": "Custom Field",
        "filters": [["dt", "in", [
            "Employee",
            "HR Request",
            "Employee Data Change Request",
        ]]],
    },
    {
        "doctype": "DocType",
        "filters": [["name", "in", [
            "HR Request",
            "Employee Data Change Request",
            "Employee Data Change Request Field",
        ]]],
    },
    {
        "doctype": "Workflow",
        "filters": [["document_type", "in", [
            "HR Request",
            "Employee Data Change Request",
        ]]],
    },
    "Workflow State",
    "Workflow Action Master",
    {
        "doctype": "Custom DocPerm",
        "filters": [["parent", "in", [
            "HR Request",
            "Employee Data Change Request",
            "Employee Data Change Request Field",
        ]]],
    },
]
```

**Verify:**

```bash
python3 -m py_compile oakglobal_erp_custom/hooks.py
```

Expected: no output.

**Commit:**

```bash
git add oakglobal_erp_custom/hooks.py
git commit -m "chore: configure HRMS fixtures"
```

---

# Task 3: Create HR roles

**Objective:** Add clean HR/security roles used by workflows and permissions.

**Implementation method:** Use Frappe console or execute script in backend. Prefer script committed later only if reusable; for initial fixture creation, DB records + export-fixtures is acceptable.

**Command:**

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend bash -lc '
cd /home/frappe/frappe-bench
bench --site erp.localhost console <<"PY"
import frappe
roles = [
    "HR Admin",
    "HR Manager",
    "Payroll Manager",
    "Payroll User",
    "Department Manager",
    "Employee Self Service",
    "Recruiter",
    "Performance Reviewer",
]
for role in roles:
    if not frappe.db.exists("Role", role):
        doc = frappe.new_doc("Role")
        doc.role_name = role
        doc.desk_access = 1
        doc.insert(ignore_permissions=True)
frappe.db.commit()
PY'
```

**Verify:**

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend \
  bench --site erp.localhost execute frappe.get_all \
  --kwargs '{"doctype":"Role","filters":{"role_name":["in",["HR Admin","HR Manager","Payroll Manager","Payroll User","Department Manager","Employee Self Service","Recruiter","Performance Reviewer"]]},"pluck":"role_name"}'
```

Expected: all 8 roles returned.

**Export fixtures:**

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend \
  bench --site erp.localhost export-fixtures
```

**Commit:**

```bash
git add oakglobal_erp_custom/fixtures/role.json
git commit -m "feat: add HRMS foundation roles"
```

---

# Task 4: Add Employee custom fields

**Objective:** Extend Employee profile for Talenta-core MVP fields without creating duplicate employee master.

**Target DocType:** `Employee`

**Fields:**

```text
hrms_foundation_section: Section Break, label HRMS Foundation
branch_location: Data, label Branch Location
work_location_type: Select, options Office\nRemote\nHybrid\nField\nBranch
compliance_section: Section Break, label Compliance
tax_status: Select, options TK/0\nTK/1\nTK/2\nTK/3\nK/0\nK/1\nK/2\nK/3
bpjs_kesehatan_no: Data, label BPJS Kesehatan No
bpjs_ketenagakerjaan_no: Data, label BPJS Ketenagakerjaan No
bank_section: Section Break, label Bank Metadata
bank_account_name: Data, label Bank Account Name
bank_account_no_masked: Data, label Bank Account No Masked
emergency_section: Section Break, label Emergency Contact Detail
emergency_contact_relation: Data, label Emergency Contact Relation
hr_lifecycle_section: Section Break, label HR Lifecycle
onboarding_status_detail: Select, options Not Started\nIn Progress\nCompleted\nBlocked
offboarding_status_detail: Select, options Not Started\nIn Progress\nCompleted\nBlocked
```

**Implementation command:**

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend bash -lc '
cd /home/frappe/frappe-bench
bench --site erp.localhost console <<"PY"
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

fields = {
    "Employee": [
        {"fieldname": "hrms_foundation_section", "label": "HRMS Foundation", "fieldtype": "Section Break", "insert_after": "job_applicant"},
        {"fieldname": "branch_location", "label": "Branch Location", "fieldtype": "Data", "insert_after": "hrms_foundation_section"},
        {"fieldname": "work_location_type", "label": "Work Location Type", "fieldtype": "Select", "options": "Office\\nRemote\\nHybrid\\nField\\nBranch", "insert_after": "branch_location"},
        {"fieldname": "compliance_section", "label": "Compliance", "fieldtype": "Section Break", "insert_after": "work_location_type"},
        {"fieldname": "tax_status", "label": "Tax Status", "fieldtype": "Select", "options": "TK/0\\nTK/1\\nTK/2\\nTK/3\\nK/0\\nK/1\\nK/2\\nK/3", "insert_after": "compliance_section"},
        {"fieldname": "bpjs_kesehatan_no", "label": "BPJS Kesehatan No", "fieldtype": "Data", "insert_after": "tax_status"},
        {"fieldname": "bpjs_ketenagakerjaan_no", "label": "BPJS Ketenagakerjaan No", "fieldtype": "Data", "insert_after": "bpjs_kesehatan_no"},
        {"fieldname": "bank_section", "label": "Bank Metadata", "fieldtype": "Section Break", "insert_after": "bpjs_ketenagakerjaan_no"},
        {"fieldname": "bank_account_name", "label": "Bank Account Name", "fieldtype": "Data", "insert_after": "bank_section"},
        {"fieldname": "bank_account_no_masked", "label": "Bank Account No Masked", "fieldtype": "Data", "insert_after": "bank_account_name"},
        {"fieldname": "emergency_section", "label": "Emergency Contact Detail", "fieldtype": "Section Break", "insert_after": "bank_account_no_masked"},
        {"fieldname": "emergency_contact_relation", "label": "Emergency Contact Relation", "fieldtype": "Data", "insert_after": "emergency_section"},
        {"fieldname": "hr_lifecycle_section", "label": "HR Lifecycle", "fieldtype": "Section Break", "insert_after": "emergency_contact_relation"},
        {"fieldname": "onboarding_status_detail", "label": "Onboarding Status Detail", "fieldtype": "Select", "options": "Not Started\\nIn Progress\\nCompleted\\nBlocked", "insert_after": "hr_lifecycle_section"},
        {"fieldname": "offboarding_status_detail", "label": "Offboarding Status Detail", "fieldtype": "Select", "options": "Not Started\\nIn Progress\\nCompleted\\nBlocked", "insert_after": "onboarding_status_detail"},
    ]
}
create_custom_fields(fields, update=True)
frappe.db.commit()
PY'
```

**Verify:**

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend \
  bench --site erp.localhost execute frappe.get_all \
  --kwargs '{"doctype":"Custom Field","filters":{"dt":"Employee","fieldname":["in",["branch_location","work_location_type","tax_status","bpjs_kesehatan_no","bpjs_ketenagakerjaan_no","bank_account_name","bank_account_no_masked","emergency_contact_relation","onboarding_status_detail","offboarding_status_detail"]]},"pluck":"fieldname"}'
```

Expected: all 10 fieldnames returned.

**Export fixtures + commit:**

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend bench --site erp.localhost export-fixtures
git add oakglobal_erp_custom/fixtures/custom_field.json
git commit -m "feat: extend Employee HRMS foundation fields"
```

---

# Task 5: Create HR Request DocType

**Objective:** Provide Talenta-style generic employee self-service request wrapper.

**DocType:** `HR Request`

**Fields:**

```text
employee: Link Employee, required
request_type: Select, required, options General\nDocument\nData Change\nAttendance\nPayroll\nBenefit\nAsset\nHelpdesk
subject: Data, required
priority: Select, options Low\nMedium\nHigh\nUrgent, default Medium
description: Small Text
attachment: Attach
requested_on: Datetime, default Now, read_only
manager_approver: Link User
hr_approver: Link User
resolution: Small Text
resolved_on: Datetime, read_only
```

**Settings:**
- `is_submittable = 1`
- `track_changes = 1`
- `allow_rename = 0`
- module: `Oakglobal ERP Custom`

**Permissions:**
- Employee Self Service: read/create/write own draft, submit
- Department Manager: read/write/submit/approve via workflow
- HR Manager: full except delete
- HR Admin: full

**Implementation note:**
- Create via Frappe UI first if faster, then export fixtures.
- Or use a Python script to insert DocType JSON.
- Keep DocType clean; do not prefix name.

**Verify:**

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend \
  bench --site erp.localhost execute frappe.db.exists --args '["DocType", "HR Request"]'
```

Expected: `HR Request` exists.

**Commit:**

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend bench --site erp.localhost export-fixtures
git add oakglobal_erp_custom/fixtures/doctype.json oakglobal_erp_custom/fixtures/custom_docperm.json
git commit -m "feat: add HR Request DocType"
```

---

# Task 6: Create Employee Data Change Request DocTypes

**Objective:** Let employees request profile changes without direct Employee edits.

**Parent DocType:** `Employee Data Change Request`

Fields:

```text
employee: Link Employee, required
reason: Small Text, required
requested_on: Datetime, default Now, read_only
changes: Table Employee Data Change Request Field
manager_approver: Link User
hr_approver: Link User
applied_on: Datetime, read_only
apply_error: Small Text, read_only
```

Settings:
- `is_submittable = 1`
- `track_changes = 1`
- module: `Oakglobal ERP Custom`

**Child DocType:** `Employee Data Change Request Field`

Fields:

```text
fieldname: Data, required
field_label: Data
old_value: Small Text, read_only
new_value: Small Text, required
```

Allowed fields initially:
- `personal_email`
- `cell_number`
- `current_address`
- `permanent_address`
- `emergency_phone_number`
- `emergency_contact_relation`
- `bank_account_name`
- `bank_account_no_masked`

Do not allow direct update to:
- salary fields
- tax status
- BPJS numbers
- company
- department
- designation
- reports_to

**Commit:**

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend bench --site erp.localhost export-fixtures
git add oakglobal_erp_custom/fixtures/doctype.json oakglobal_erp_custom/fixtures/custom_docperm.json
git commit -m "feat: add Employee Data Change Request DocTypes"
```

---

# Task 7: Add workflows

**Objective:** Enforce approval path for requests.

## Workflow A: HR Request Workflow

Document Type: `HR Request`

States:
- Draft
- Submitted
- Manager Approved
- HR Approved
- Rejected
- Cancelled

Actions:
- Submit: Draft -> Submitted, allowed: Employee Self Service, HR Manager, HR Admin
- Manager Approve: Submitted -> Manager Approved, allowed: Department Manager
- HR Approve: Manager Approved -> HR Approved, allowed: HR Manager, HR Admin
- Reject: Submitted/Manager Approved -> Rejected, allowed: Department Manager, HR Manager, HR Admin
- Cancel: Submitted/Manager Approved -> Cancelled, allowed: HR Manager, HR Admin

## Workflow B: Employee Data Change Request Workflow

Same states/actions.

Additional rule:
- Employee update applies only after HR Approved.
- Implementation can be added in Sprint 2B server hook if not done in Sprint 2A.

**Export + commit:**

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend bench --site erp.localhost export-fixtures
git add oakglobal_erp_custom/fixtures/workflow.json oakglobal_erp_custom/fixtures/workflow_state.json oakglobal_erp_custom/fixtures/workflow_action_master.json
git commit -m "feat: add HRMS foundation workflows"
```

---

# Task 8: Add server-side apply logic for Employee Data Change Request

**Objective:** On HR approval, apply allowed field changes safely to Employee.

**Files:**
- Create: `oakglobal_erp_custom/hrms_ext/__init__.py`
- Create: `oakglobal_erp_custom/hrms_ext/employee_data_change.py`
- Modify: `oakglobal_erp_custom/hooks.py`

**Hook:**

```python
doc_events = {
    "Employee Data Change Request": {
        "on_update": "oakglobal_erp_custom.hrms_ext.employee_data_change.apply_approved_changes",
    }
}
```

**Implementation:**

```python
import frappe

ALLOWED_EMPLOYEE_FIELDS = {
    "personal_email",
    "cell_number",
    "current_address",
    "permanent_address",
    "emergency_phone_number",
    "emergency_contact_relation",
    "bank_account_name",
    "bank_account_no_masked",
}


def apply_approved_changes(doc, method=None):
    if doc.workflow_state != "HR Approved":
        return
    if doc.applied_on:
        return

    employee = frappe.get_doc("Employee", doc.employee)

    for row in doc.changes:
        if row.fieldname not in ALLOWED_EMPLOYEE_FIELDS:
            frappe.throw(f"Field not allowed for employee self-service update: {row.fieldname}")
        employee.set(row.fieldname, row.new_value)

    employee.save(ignore_permissions=True)
    doc.db_set("applied_on", frappe.utils.now(), update_modified=False)
```

**Test plan:**
- Create draft request with allowed field.
- Move to HR Approved.
- Verify Employee field updated.
- Try disallowed field and expect error.

**Commit:**

```bash
git add oakglobal_erp_custom/hrms_ext oakglobal_erp_custom/hooks.py
git commit -m "feat: apply approved employee data changes"
```

---

# Task 9: Final migrate/export/verify

**Objective:** Ensure Sprint 2 is portable and clean.

**Commands:**

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend \
  bench --site erp.localhost migrate

docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend \
  bench --site erp.localhost clear-cache

docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend \
  bench --site erp.localhost export-fixtures

git diff --check
git status --short
```

Verify DocTypes:

```bash
docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend \
  bench --site erp.localhost execute frappe.db.exists --args '["DocType", "HR Request"]'

docker compose --project-name oaklocal -f ~/oak_erp/local/compose.yaml exec -T backend \
  bench --site erp.localhost execute frappe.db.exists --args '["DocType", "Employee Data Change Request"]'
```

Verify fixtures are present:

```bash
ls -la oakglobal_erp_custom/fixtures
python3 -m json.tool oakglobal_erp_custom/fixtures/custom_field.json >/dev/null
python3 -m json.tool oakglobal_erp_custom/fixtures/doctype.json >/dev/null
```

Final commit if any leftover:

```bash
git add oakglobal_erp_custom docs/hrms
git commit -m "feat: complete HRMS foundation sprint"
git push origin dev
```

---

## Risks and Controls

Risk: fixture export pulls unrelated records.
- Control: use filtered fixtures in `hooks.py`.

Risk: employees update sensitive fields.
- Control: whitelist allowed fields in server code.

Risk: workflow state names mismatch server hook.
- Control: verify exact state `HR Approved` in Workflow fixture.

Risk: DocType created through UI not committed.
- Control: run `bench export-fixtures`, commit fixture JSON.

Risk: payroll fields exposed to ESS.
- Control: do not include payroll/tax/BPJS in Employee Data Change Request allowed fields.

---

## Definition of Done

Sprint 2 done when:
- roles exist and exported
- Employee custom fields exist and exported
- `HR Request` exists and exported
- `Employee Data Change Request` + child table exist and exported
- workflows exist and exported
- approved data-change request can update allowed Employee fields
- disallowed field update is blocked
- `bench migrate` passes
- `git diff --check` passes
- branch `dev` pushed
