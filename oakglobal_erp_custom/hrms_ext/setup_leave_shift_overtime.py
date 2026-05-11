import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import field


def ensure_custom_doctype(name, fields, perms, submit=0):
    if frappe.db.exists('DocType', name):
        return
    d = frappe.new_doc('DocType')
    d.name = name
    d.module = 'Oakglobal ERP Custom'
    d.custom = 1
    d.is_submittable = submit
    d.track_changes = 1
    d.allow_rename = 0
    for f in fields:
        d.append('fields', f)
    for p in perms:
        d.append('permissions', p)
    d.insert(ignore_permissions=True)


def ensure_request_doctypes():
    perms = [
        {'role': 'Employee Self Service', 'read': 1, 'write': 1, 'create': 1, 'submit': 1},
        {'role': 'Department Manager', 'read': 1, 'write': 1, 'submit': 1},
        {'role': 'HR Manager', 'read': 1, 'write': 1, 'create': 1, 'submit': 1, 'cancel': 1, 'amend': 1},
        {'role': 'HR Admin', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'submit': 1, 'cancel': 1, 'amend': 1},
        {'role': 'System Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'submit': 1, 'cancel': 1, 'amend': 1},
    ]

    ensure_custom_doctype('Shift Change Request', [
        field('employee', 'Employee', 'Link', options='Employee', reqd=1, in_list_view=1),
        field('current_shift', 'Current Shift', 'Link', options='Shift Type'),
        field('requested_shift', 'Requested Shift', 'Link', options='Shift Type', reqd=1, in_list_view=1),
        field('effective_date', 'Effective Date', 'Date', reqd=1, in_list_view=1),
        field('reason', 'Reason', 'Small Text', reqd=1),
        field('manager_approval', 'Manager Approval', 'Select', options='Pending\nApproved\nRejected', default='Pending', read_only=1, in_list_view=1),
        field('hr_approval', 'HR Approval', 'Select', options='Pending\nApproved\nRejected', default='Pending', read_only=1, in_list_view=1),
        field('decision_note', 'Decision Note', 'Small Text'),
    ], perms, submit=1)

    ensure_custom_doctype('Attendance Correction Request', [
        field('employee', 'Employee', 'Link', options='Employee', reqd=1, in_list_view=1),
        field('attendance_date', 'Attendance Date', 'Date', reqd=1, in_list_view=1),
        field('requested_log_type', 'Requested Log Type', 'Select', options='IN\nOUT', reqd=1, in_list_view=1),
        field('requested_time', 'Requested Time', 'Datetime', reqd=1, in_list_view=1),
        field('reason', 'Reason', 'Small Text', reqd=1),
        field('evidence', 'Evidence', 'Attach'),
        field('manager_approval', 'Manager Approval', 'Select', options='Pending\nApproved\nRejected', default='Pending', read_only=1, in_list_view=1),
        field('hr_approval', 'HR Approval', 'Select', options='Pending\nApproved\nRejected', default='Pending', read_only=1, in_list_view=1),
        field('decision_note', 'Decision Note', 'Small Text'),
    ], perms, submit=1)


def ensure_overtime_extensions():
    create_custom_fields({
        'Overtime Slip': [
            field('approval_summary_section', 'Approval Summary', 'Section Break', insert_after='overtime_details'),
            field('manager_approval', 'Manager Approval', 'Select', options='Pending\nApproved\nRejected', default='Pending', read_only=1, insert_after='approval_summary_section'),
            field('hr_approval', 'HR Approval', 'Select', options='Pending\nApproved\nRejected', default='Pending', read_only=1, insert_after='manager_approval'),
            field('approval_decision_note', 'Approval Decision Note', 'Small Text', read_only=1, insert_after='hr_approval'),
            field('payroll_trace_link', 'Payroll Trace Link', 'Link', options='Payroll Source Trace', read_only=1, insert_after='approval_decision_note'),
        ]
    }, update=True)


def run():
    ensure_request_doctypes()
    ensure_overtime_extensions()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    run()
    for dt in ['Shift Change Request', 'Attendance Correction Request']:
        if not frappe.db.exists('DocType', dt):
            raise Exception(f'missing doctype {dt}')
    for fn in ['manager_approval', 'hr_approval', 'payroll_trace_link']:
        if not frappe.db.exists('Custom Field', {'dt': 'Overtime Slip', 'fieldname': fn}):
            raise Exception(f'missing Overtime Slip.{fn}')
    frappe.db.rollback()
    return 'LEAVE_SHIFT_OVERTIME_SETUP_SMOKE_OK'
