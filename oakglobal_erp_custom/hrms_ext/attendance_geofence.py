import frappe

from oakglobal_erp_custom.hrms_ext.setup_attendance_geofence import distance_meters


def _has_value(value):
    return value not in (None, "")


def _get_rule(attendance_location=None, work_location_type=None):
    filters = {"is_active": 1}
    if attendance_location:
        filters["attendance_location"] = attendance_location
        rule = frappe.get_all("Attendance Validation Rule", filters=filters, fields=["*"], limit_page_length=1)
        if rule:
            return frappe._dict(rule[0])
    if work_location_type:
        rule = frappe.get_all(
            "Attendance Validation Rule",
            filters={"is_active": 1, "work_location_type": work_location_type},
            fields=["*"],
            limit_page_length=1,
        )
        if rule:
            return frappe._dict(rule[0])
    return None


def _get_active_geofence(attendance_location):
    if not attendance_location:
        return None
    geofences = frappe.get_all(
        "Attendance Geofence",
        filters={"attendance_location": attendance_location, "is_active": 1},
        fields=["name", "latitude", "longitude", "radius_meters"],
        order_by="modified desc",
        limit_page_length=1,
    )
    return frappe._dict(geofences[0]) if geofences else None


def validate_checkin(doc, method=None):
    """Validate Employee Checkin geofence metadata without touching HRMS core."""
    if not getattr(doc, "attendance_location", None):
        doc.validation_status = "Pending"
        doc.validation_message = "No attendance location selected."
        return

    employee_work_type = None
    if getattr(doc, "employee", None):
        employee_work_type = frappe.db.get_value("Employee", doc.employee, "work_location_type")
    rule = _get_rule(doc.attendance_location, employee_work_type)
    geofence = _get_active_geofence(doc.attendance_location)

    if not geofence:
        doc.validation_status = "Manual Review"
        doc.validation_message = "No active geofence found for attendance location."
        return

    doc.attendance_geofence = geofence.name
    lat = doc.captured_latitude if _has_value(getattr(doc, "captured_latitude", None)) else getattr(doc, "latitude", None)
    lon = doc.captured_longitude if _has_value(getattr(doc, "captured_longitude", None)) else getattr(doc, "longitude", None)

    if not (_has_value(lat) and _has_value(lon)):
        doc.validation_status = "Missing Location"
        doc.validation_message = "GPS coordinates missing."
        return

    dist = distance_meters(lat, lon, geofence.latitude, geofence.longitude)
    doc.distance_from_geofence_meters = round(dist, 2)
    allowed_radius = geofence.radius_meters or 0
    if rule and rule.max_distance_override_meters:
        allowed_radius = rule.max_distance_override_meters

    if rule and rule.require_selfie and not getattr(doc, "selfie_image", None):
        doc.validation_status = "Manual Review"
        doc.validation_message = "Selfie required by attendance validation rule."
        return

    if dist <= allowed_radius:
        doc.validation_status = "Valid"
        doc.validation_message = f"Inside geofence ({round(dist, 2)} m <= {allowed_radius} m)."
        return

    if rule and rule.allow_outside_geofence:
        doc.validation_status = "Manual Review"
        doc.validation_message = f"Outside geofence but allowed for manual review ({round(dist, 2)} m > {allowed_radius} m)."
        return

    doc.validation_status = "Outside Geofence"
    doc.validation_message = f"Outside geofence ({round(dist, 2)} m > {allowed_radius} m)."


def log_checkin_validation(doc, method=None):
    if not getattr(doc, "name", None) or not frappe.db.exists("DocType", "Attendance Validation Log"):
        return
    if frappe.db.exists("Attendance Validation Log", {"employee_checkin": doc.name}):
        return
    log = frappe.new_doc("Attendance Validation Log")
    log.employee_checkin = doc.name
    log.employee = getattr(doc, "employee", None)
    log.attendance_location = getattr(doc, "attendance_location", None)
    log.attendance_geofence = getattr(doc, "attendance_geofence", None)
    log.validation_status = getattr(doc, "validation_status", None)
    log.distance_from_geofence_meters = getattr(doc, "distance_from_geofence_meters", None)
    log.captured_latitude = getattr(doc, "captured_latitude", None) or getattr(doc, "latitude", None)
    log.captured_longitude = getattr(doc, "captured_longitude", None) or getattr(doc, "longitude", None)
    log.validation_message = getattr(doc, "validation_message", None)
    log.insert(ignore_permissions=True)


def create_exception_for_checkin(employee_checkin, reason, evidence=None):
    checkin = frappe.get_doc("Employee Checkin", employee_checkin)
    if checkin.validation_status not in ("Manual Review", "Outside Geofence", "Missing Location"):
        frappe.throw("Only Manual Review, Outside Geofence, or Missing Location checkins need exception approval.")
    existing = getattr(checkin, "validation_exception", None)
    if existing:
        return existing
    exc = frappe.new_doc("Attendance Validation Exception")
    exc.employee_checkin = checkin.name
    exc.employee = checkin.employee
    exc.exception_status = "Pending Approval"
    exc.reason = reason
    exc.evidence = evidence
    exc.insert(ignore_permissions=True)
    frappe.db.set_value("Employee Checkin", checkin.name, {
        "validation_exception": exc.name,
        "validation_override_status": "Pending Approval",
    })
    return exc.name


def approve_exception(exception_name, decision_note=None):
    exc = frappe.get_doc("Attendance Validation Exception", exception_name)
    exc.exception_status = "Approved"
    exc.approver = frappe.session.user
    exc.decision_on = frappe.utils.now()
    exc.decision_note = decision_note
    exc.save(ignore_permissions=True)
    frappe.db.set_value("Employee Checkin", exc.employee_checkin, "validation_override_status", "Approved")
    return exc.name


def reject_exception(exception_name, decision_note=None):
    exc = frappe.get_doc("Attendance Validation Exception", exception_name)
    exc.exception_status = "Rejected"
    exc.approver = frappe.session.user
    exc.decision_on = frappe.utils.now()
    exc.decision_note = decision_note
    exc.save(ignore_permissions=True)
    frappe.db.set_value("Employee Checkin", exc.employee_checkin, "validation_override_status", "Rejected")
    return exc.name


def smoke_test():
    from oakglobal_erp_custom.hrms_ext.setup_attendance_approval import run as setup_approval

    setup_approval()
    company = frappe.get_all("Company", pluck="name", limit_page_length=1)[0]

    loc = frappe.new_doc("Attendance Location")
    loc.location_name = "Smoke Approval Office"
    loc.location_type = "Office"
    loc.company = company
    loc.insert(ignore_permissions=True)

    gf = frappe.new_doc("Attendance Geofence")
    gf.attendance_location = loc.name
    gf.latitude = -6.200000
    gf.longitude = 106.816666
    gf.radius_meters = 150
    gf.insert(ignore_permissions=True)

    emp = frappe.new_doc("Employee")
    emp.first_name = "Smoke"
    emp.last_name = "Approval"
    emp.gender = "Male"
    emp.date_of_birth = "1990-01-01"
    emp.date_of_joining = "2026-01-01"
    emp.company = company
    emp.insert(ignore_permissions=True)

    checkin = frappe.new_doc("Employee Checkin")
    checkin.employee = emp.name
    checkin.time = "2026-01-01 08:03:00"
    checkin.log_type = "IN"
    checkin.attendance_location = loc.name
    checkin.captured_latitude = -6.250000
    checkin.captured_longitude = 106.900000
    checkin.insert(ignore_permissions=True)
    if checkin.validation_status != "Outside Geofence":
        raise Exception(f"outside checkin not flagged: {checkin.validation_status}")
    log_checkin_validation(checkin)
    if not frappe.db.exists("Attendance Validation Log", {"employee_checkin": checkin.name}):
        raise Exception("validation log not created")
    exc_name = create_exception_for_checkin(checkin.name, "Smoke approval")
    approve_exception(exc_name, "Smoke approved")
    if frappe.db.get_value("Employee Checkin", checkin.name, "validation_override_status") != "Approved":
        raise Exception("exception approval did not update checkin")
    frappe.db.rollback()
    return "ATTENDANCE_APPROVAL_SMOKE_OK"
