import frappe


def create_trace(employee, period_start, period_end, source_doctype, source_name, source_type=None, **kw):
    existing = frappe.db.exists("Payroll Source Trace", {
        "employee": employee,
        "period_start": period_start,
        "period_end": period_end,
        "source_doctype": source_doctype,
        "source_name": source_name,
    })
    if existing:
        return existing
    trace = frappe.new_doc("Payroll Source Trace")
    trace.employee = employee
    trace.company = kw.get("company") or frappe.db.get_value("Employee", employee, "company")
    trace.period_start = period_start
    trace.period_end = period_end
    trace.source_type = source_type or source_doctype
    trace.source_doctype = source_doctype
    trace.source_name = source_name
    trace.source_date = kw.get("source_date")
    trace.source_status = kw.get("source_status")
    trace.quantity = kw.get("quantity")
    trace.amount = kw.get("amount")
    trace.salary_slip = kw.get("salary_slip")
    trace.payroll_entry = kw.get("payroll_entry")
    trace.trace_note = kw.get("trace_note")
    trace.insert(ignore_permissions=True)
    return trace.name


def build_attendance_traces(employee, period_start, period_end, salary_slip=None):
    names = []
    checkins = frappe.get_all(
        "Employee Checkin",
        filters={"employee": employee, "time": ["between", [period_start, period_end]]},
        fields=["name", "time", "validation_status", "validation_override_status"],
        order_by="time asc",
        limit_page_length=1000,
    )
    for c in checkins:
        status = c.validation_status or "Unvalidated"
        note = f"Checkin {status}"
        if c.validation_override_status and c.validation_override_status != "None":
            note += f", override {c.validation_override_status}"
        names.append(create_trace(
            employee,
            period_start,
            period_end,
            "Employee Checkin",
            c.name,
            source_type="Employee Checkin",
            source_date=c.time.date() if hasattr(c.time, "date") else str(c.time)[:10],
            source_status=status,
            salary_slip=salary_slip,
            trace_note=note,
        ))
    exceptions = frappe.get_all(
        "Attendance Validation Exception",
        filters={"employee": employee},
        fields=["name", "employee_checkin", "exception_status", "decision_on"],
        limit_page_length=1000,
    ) if frappe.db.exists("DocType", "Attendance Validation Exception") else []
    checkin_names = {c.name for c in checkins}
    for e in exceptions:
        if e.employee_checkin not in checkin_names:
            continue
        names.append(create_trace(
            employee,
            period_start,
            period_end,
            "Attendance Validation Exception",
            e.name,
            source_type="Attendance Validation Exception",
            source_date=e.decision_on.date() if getattr(e, "decision_on", None) and hasattr(e.decision_on, "date") else None,
            source_status=e.exception_status,
            salary_slip=salary_slip,
            trace_note=f"Attendance exception {e.exception_status}",
        ))
    return names


def update_salary_slip_trace_summary(salary_slip):
    slip = frappe.get_doc("Salary Slip", salary_slip)
    traces = frappe.get_all("Payroll Source Trace", filters={"salary_slip": salary_slip}, fields=["source_type"])
    attendance_count = sum(1 for t in traces if t.source_type == "Employee Checkin")
    exception_count = sum(1 for t in traces if t.source_type == "Attendance Validation Exception")
    slip.payroll_trace_generated_on = frappe.utils.now()
    slip.attendance_source_count = attendance_count
    slip.exception_source_count = exception_count
    slip.payroll_trace_note = f"Trace records: {len(traces)}"
    slip.save(ignore_permissions=True)
    return {"attendance_source_count": attendance_count, "exception_source_count": exception_count, "total": len(traces)}


def smoke_test():
    from oakglobal_erp_custom.hrms_ext.setup_payroll_traceability import run as setup_trace
    from oakglobal_erp_custom.hrms_ext.setup_attendance_approval import run as setup_approval
    from oakglobal_erp_custom.hrms_ext.attendance_geofence import validate_checkin, log_checkin_validation, create_exception_for_checkin, approve_exception

    setup_approval()
    setup_trace()
    company = frappe.get_all("Company", pluck="name", limit_page_length=1)[0]
    emp = frappe.new_doc("Employee")
    emp.first_name = "Smoke"
    emp.last_name = "Payroll Trace"
    emp.gender = "Male"
    emp.date_of_birth = "1990-01-01"
    emp.date_of_joining = "2026-01-01"
    emp.company = company
    emp.insert(ignore_permissions=True)

    loc = frappe.new_doc("Attendance Location")
    loc.location_name = "Smoke Payroll Trace Office"
    loc.location_type = "Office"
    loc.company = company
    loc.insert(ignore_permissions=True)
    gf = frappe.new_doc("Attendance Geofence")
    gf.attendance_location = loc.name
    gf.latitude = -6.200000
    gf.longitude = 106.816666
    gf.radius_meters = 150
    gf.insert(ignore_permissions=True)

    checkin = frappe.new_doc("Employee Checkin")
    checkin.employee = emp.name
    checkin.time = "2026-01-02 08:00:00"
    checkin.log_type = "IN"
    checkin.attendance_location = loc.name
    checkin.captured_latitude = -6.250000
    checkin.captured_longitude = 106.900000
    validate_checkin(checkin)
    checkin.insert(ignore_permissions=True)
    log_checkin_validation(checkin)
    exc = create_exception_for_checkin(checkin.name, "Smoke payroll trace")
    approve_exception(exc, "Approved for payroll trace smoke")

    traces = build_attendance_traces(emp.name, "2026-01-01", "2026-01-31")
    if len(traces) < 2:
        raise Exception(f"expected checkin and exception traces, got {len(traces)}")
    frappe.db.rollback()
    return "PAYROLL_TRACE_SMOKE_OK"
