import math
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def field(fieldname, label, fieldtype, **kw):
    d = {"fieldname": fieldname, "label": label, "fieldtype": fieldtype}
    d.update(kw)
    return d


def ensure_doctype(name, fields, perms, istable=0):
    if frappe.db.exists("DocType", name):
        return
    d = frappe.new_doc("DocType")
    d.name = name
    d.module = "Oakglobal ERP Custom"
    d.custom = 1
    d.istable = istable
    d.track_changes = 1
    d.allow_rename = 0
    for f in fields:
        d.append("fields", f)
    for p in perms:
        d.append("permissions", p)
    d.insert(ignore_permissions=True)


def ensure_attendance_doctypes():
    perms = [
        {"role": "HR Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "HR Manager", "read": 1, "write": 1, "create": 1},
        {"role": "Department Manager", "read": 1},
        {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
    ]
    ensure_doctype("Attendance Location", [
        field("location_name", "Location Name", "Data", reqd=1, in_list_view=1),
        field("location_type", "Location Type", "Select", options="Office\nBranch\nRemote\nField\nClient Site", reqd=1, in_list_view=1),
        field("company", "Company", "Link", options="Company", in_list_view=1),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("address", "Address", "Small Text"),
    ], perms)
    ensure_doctype("Attendance Geofence", [
        field("attendance_location", "Attendance Location", "Link", options="Attendance Location", reqd=1, in_list_view=1),
        field("latitude", "Latitude", "Float", reqd=1),
        field("longitude", "Longitude", "Float", reqd=1),
        field("radius_meters", "Radius Meters", "Int", default=100, reqd=1),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
        field("notes", "Notes", "Small Text"),
    ], perms)
    ensure_doctype("Attendance Validation Rule", [
        field("rule_name", "Rule Name", "Data", reqd=1, in_list_view=1),
        field("attendance_location", "Attendance Location", "Link", options="Attendance Location", in_list_view=1),
        field("work_location_type", "Work Location Type", "Select", options="Office\nRemote\nHybrid\nField\nBranch", in_list_view=1),
        field("require_geofence", "Require Geofence", "Check", default=1),
        field("require_selfie", "Require Selfie", "Check", default=0),
        field("allow_outside_geofence", "Allow Outside Geofence", "Check", default=0),
        field("max_distance_override_meters", "Max Distance Override Meters", "Int"),
        field("is_active", "Is Active", "Check", default=1, in_list_view=1),
    ], perms)


def ensure_attendance_fields():
    create_custom_fields({
        "Employee Checkin": [
            field("geofence_section", "Geofence Validation", "Section Break", insert_after="skip_auto_attendance"),
            field("attendance_location", "Attendance Location", "Link", options="Attendance Location", insert_after="geofence_section"),
            field("attendance_geofence", "Attendance Geofence", "Link", options="Attendance Geofence", insert_after="attendance_location"),
            field("captured_latitude", "Captured Latitude", "Float", insert_after="attendance_geofence"),
            field("captured_longitude", "Captured Longitude", "Float", insert_after="captured_latitude"),
            field("distance_from_geofence_meters", "Distance From Geofence Meters", "Float", read_only=1, insert_after="captured_longitude"),
            field("validation_status", "Validation Status", "Select", options="Pending\nValid\nOutside Geofence\nMissing Location\nManual Review", default="Pending", in_list_view=1, insert_after="distance_from_geofence_meters"),
            field("selfie_image", "Selfie Image", "Attach Image", insert_after="validation_status"),
            field("attendance_device_id", "Attendance Device ID", "Data", insert_after="selfie_image"),
            field("device_platform", "Device Platform", "Data", insert_after="attendance_device_id"),
            field("validation_message", "Validation Message", "Small Text", read_only=1, insert_after="device_platform"),
        ],
        "Attendance Request": [
            field("geofence_exception_section", "Geofence Exception", "Section Break", insert_after="reason"),
            field("attendance_location", "Attendance Location", "Link", options="Attendance Location", insert_after="geofence_exception_section"),
            field("captured_latitude", "Captured Latitude", "Float", insert_after="attendance_location"),
            field("captured_longitude", "Captured Longitude", "Float", insert_after="captured_latitude"),
            field("geofence_exception_reason", "Geofence Exception Reason", "Select", options="Remote Work\nField Work\nClient Visit\nDevice Issue\nGPS Issue\nManual Correction", insert_after="captured_longitude"),
            field("geofence_evidence", "Geofence Evidence", "Attach", insert_after="geofence_exception_reason"),
        ],
    }, update=True)


def distance_meters(lat1, lon1, lat2, lon2):
    r = 6371000
    p1, p2 = math.radians(float(lat1)), math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def validate_point(lat, lon, geofence):
    gf = frappe.get_doc("Attendance Geofence", geofence)
    dist = distance_meters(lat, lon, gf.latitude, gf.longitude)
    return {"distance": dist, "valid": dist <= (gf.radius_meters or 0)}


def run():
    ensure_attendance_doctypes()
    ensure_attendance_fields()
    frappe.db.commit()
    frappe.clear_cache()


def smoke_test():
    company = frappe.get_all("Company", pluck="name", limit_page_length=1)[0]
    loc = frappe.new_doc("Attendance Location")
    loc.location_name = "Smoke Office"
    loc.location_type = "Office"
    loc.company = company
    loc.insert(ignore_permissions=True)
    gf = frappe.new_doc("Attendance Geofence")
    gf.attendance_location = loc.name
    gf.latitude = -6.200000
    gf.longitude = 106.816666
    gf.radius_meters = 150
    gf.insert(ignore_permissions=True)
    inside = validate_point(-6.200100, 106.816700, gf.name)
    outside = validate_point(-6.250000, 106.900000, gf.name)
    if not inside["valid"]:
        raise Exception(f"inside point rejected: {inside}")
    if outside["valid"]:
        raise Exception(f"outside point accepted: {outside}")
    for dt in ["Employee Checkin", "Attendance Request"]:
        for fn in ["attendance_location", "captured_latitude", "captured_longitude"]:
            if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fn}):
                raise Exception(f"missing custom field {dt}.{fn}")
    frappe.db.rollback()
    return "ATTENDANCE_GEOFENCE_SMOKE_OK"
