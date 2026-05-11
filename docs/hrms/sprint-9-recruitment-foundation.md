# Sprint 9 Recruitment Foundation

Goal: extend Talenta P1 recruitment coverage using standard HRMS recruitment DocTypes first, with core-safe custom scoring and assessment layers.

Deliverables:
- Extend Job Opening with staffing/requisition/pipeline control fields
- Extend Job Applicant with screening, assessment summary, score average, onboarding handoff status
- Extend Job Offer with Employee Onboarding handoff reference
- Custom DocType Recruitment Pipeline Rule
- Custom DocType Applicant Assessment
- Custom DocType Candidate Scorecard

Scope:
- no ERPNext/HRMS core edits
- no AI scoring yet
- no automatic applicant-to-employee creation yet
- setup + fixtures only

Smoke tests:
- setup creates recruitment custom DocTypes
- setup adds recruitment custom fields to standard HRMS DocTypes
