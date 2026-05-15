import frappe
from frappe import _


def validate_quotation(doc, method=None):
    if not doc.get("job_service_type"):
        frappe.throw(_("Job Service Type is required for Quotation."))

    service = frappe.get_cached_doc("Job Service Type", doc.job_service_type)

    if service.requires_route and not doc.get("route_legs"):
        frappe.throw(_("At least one Route Leg is required for {0}.").format(service.service_name))

    if service.requires_package_detail and not doc.get("package_details"):
        frappe.throw(_("At least one Package Detail is required for {0}.").format(service.service_name))

    if service.requires_trip_count and (not doc.get("total_trips") or doc.total_trips <= 0):
        frappe.throw(_("Total Trips must be greater than zero for {0}.").format(service.service_name))

    if service.service_code == "DTD":
        roles = {row.location_role for row in doc.get("route_legs", []) if row.location_role}
        leg_types = {row.leg_type for row in doc.get("route_legs", []) if row.leg_type}

        if not (({"POL", "Origin"} & roles) or ("Loading" in leg_types)):
            frappe.msgprint(
                _("Door to Door quotation should include Loading/POL or Origin route leg."),
                indicator="orange",
                alert=True,
            )

        if not (({"POD", "Destination"} & roles) or ("Unloading" in leg_types)):
            frappe.msgprint(
                _("Door to Door quotation should include Unloading/POD or Destination route leg."),
                indicator="orange",
                alert=True,
            )
