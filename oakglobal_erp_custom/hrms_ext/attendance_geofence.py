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


def smoke_test():
    company = frappe.get_all("Company", pluck="name", limit_page_length=1)[0]

    loc = frappe.new_doc("Attendance Location")
    loc.location_name = "Smoke Validation Office"
    loc.location_type = "Office"
    loc.company = company
    loc.insert(ignore_permissions=True)

    gf = frappe.new_doc("Attendance Geofence")
    gf.attendance_location = loc.name
    gf.latitude = -6.200000
    gf.longitude = 106.816666
    gf.radius_meters = 150
    gf.insert(ignore_permissions=True)

    rule = frappe.new_doc("Attendance Validation Rule")
    rule.rule_name = "Smoke Office Rule"
    rule.attendance_location = loc.name
    rule.require_geofence = 1
    rule.require_selfie = 0
    rule.allow_outside_geofence = 0
    rule.insert(ignore_permissions=True)

    emp = frappe.new_doc("Employee")
    emp.first_name = "Smoke"
    emp.last_name = "Attendance"
    emp.gender = "Male"
    emp.date_of_birth = "1990-01-01"
    emp.date_of_joining = "2026-01-01"
    emp.company = company
    emp.insert(ignore_permissions=True)

    inside = frappe.new_doc("Employee Checkin")
    inside.employee = emp.name
    inside.time = "2026-01-01 08:00:00"
    inside.log_type = "IN"
    inside.attendance_location = loc.name
    inside.captured_latitude = -6.200100
    inside.captured_longitude = 106.816700
    validate_checkin(inside)
    if inside.validation_status != "Valid":
        raise Exception(f"inside checkin not valid: {inside.validation_status} {inside.validation_message}")

    outside = frappe.new_doc("Employee Checkin")
    outside.employee = emp.name
    outside.time = "2026-01-01 08:01:00"
    outside.log_type = "IN"
    outside.attendance_location = loc.name
    outside.captured_latitude = -6.250000
    outside.captured_longitude = 106.900000
    validate_checkin(outside)
    if outside.validation_status != "Outside Geofence":
        raise Exception(f"outside checkin not blocked: {outside.validation_status} {outside.validation_message}")

    missing = frappe.new_doc("Employee Checkin")
    missing.employee = emp.name
    missing.time = "2026-01-01 08:02:00"
    missing.log_type = "IN"
    missing.attendance_location = loc.name
    validate_checkin(missing)
    if missing.validation_status != "Missing Location":
        raise Exception(f"missing location not detected: {missing.validation_status}")

    frappe.db.rollback()
    return "ATTENDANCE_VALIDATION_SMOKE_OK"
