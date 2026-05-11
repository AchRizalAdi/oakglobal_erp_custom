# Sprint 10 Analytics and Integration Foundation

Goal: complete Talenta MVP foundation with analytics/integration data structures for webhooks, logs, attendance device imports, and payroll journal mapping.

Deliverables:
- Custom DocType Webhook Endpoint
- Custom DocType Integration Log
- Custom DocType External Attendance Import
- Custom DocType Attendance Device
- Custom DocType Device Integration Setting
- Custom DocType Payroll Journal Mapping

Analytics foundation:
- Sprint 10 prepares clean source data for later Query Reports and dashboards:
  - headcount
  - attendance
  - payroll cost
  - overtime
  - recruitment funnel
  - integration failures

Scope:
- no ERPNext/HRMS core edits
- no secrets in fixtures
- no live external API calls yet
- no scheduler jobs yet
- setup + fixtures only

Smoke tests:
- setup creates all Sprint 10 integration DocTypes
- fixture export includes all Sprint 10 DocTypes
