# Sprint 19 Talent Development Foundation

## Goal
Add talent development foundation for performance, OKR, competency, and development planning while keeping official HRMS DocTypes as base.

## Scope
- Custom DocType `OKR Cycle`
- Custom DocType `Competency Map`
- Custom DocType `Individual Development Plan`
- Custom fields on official `Appraisal`
- Custom fields on official `Goal`
- Custom fields on official `Training Program`
- Fixture filters updated

## Non-goals
- No replacement of official HRMS appraisal, goal, skill, or training DocTypes.
- No AI performance summary.
- No LMS/course engine.
- No succession planning.
- No ERPNext/HRMS core edits.

## Controls
- `OKR Cycle` defines review period and status.
- `Competency Map` links department/designation/skill to required capability level.
- `Individual Development Plan` links employee, appraisal, goal, competency, training program, mentor, status, and progress.
- Official `Appraisal`, `Goal`, and `Training Program` remain canonical HRMS records.

## Validation
Run:

```bash
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_talent_development.smoke_test
bench --site erp.localhost execute oakglobal_erp_custom.hrms_ext.setup_talent_development.run
bench --site erp.localhost export-fixtures
```

Expected:

```text
TALENT_DEVELOPMENT_SETUP_SMOKE_OK
```
