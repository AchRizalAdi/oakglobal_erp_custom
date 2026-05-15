import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

SERVICE_TYPES = [
    ("DTD", "Door to Door", "Multimodal", 1, 1, 1),
    ("PTP", "Port to Port", "Sea Freight", 1, 1, 0),
    ("DTP", "Door to Port", "Multimodal", 1, 1, 1),
    ("PTD", "Port to Door", "Multimodal", 1, 1, 1),
    ("TRK", "Trucking Only", "Trucking", 1, 0, 1),
    ("SEA", "Sea Freight", "Sea Freight", 1, 1, 0),
    ("CCL", "Custom Clearance", "Custom Clearance", 0, 0, 0),
    ("WHS", "Warehouse Handling", "Warehouse", 0, 0, 0),
    ("ISO", "Isotank Rental", "Other", 0, 1, 0),
]

TRANSPORT_MODES = "\n".join([
    "Trucking",
    "Sea Freight",
    "Air Freight",
    "Multimodal",
    "Custom Clearance",
    "Warehouse",
    "Other",
])
LEG_TYPES = "\n".join([
    "Loading",
    "Pickup",
    "Transit",
    "Port",
    "Warehouse",
    "Customs",
    "Unloading",
    "Delivery",
])
LOCATION_ROLES = "\n".join([
    "POL",
    "POD",
    "Origin",
    "Destination",
    "Transit Port",
    "Warehouse",
    "Customs Office",
    "Depot",
    "Other",
])
CHARGE_TYPES = "\n".join([
    "VAT",
    "Overtime",
    "Storage",
    "Demurrage",
    "Detention",
    "Insurance",
    "Fuel Adjustment",
    "Toll Fee",
    "Port Charge",
    "Custom Clearance",
    "Documentation Fee",
    "Other",
])

LOGISTICS_PRINT_HTML = r"""
<h2>Quotation</h2>
<p><b>Quotation No:</b> {{ doc.name }}<br>
<b>Date:</b> {{ frappe.format(doc.transaction_date, {'fieldtype':'Date'}) }}<br>
<b>Customer:</b> {{ doc.customer_name or doc.party_name }}</p>

<h3>{{ doc.job_service_title or doc.job_service_type or 'Logistics Service' }}</h3>
<p><b>Commodity:</b> {{ doc.commodity or '' }}<br>
<b>Total Quantity:</b> {{ doc.total_quantity or '' }} {{ doc.quantity_uom or '' }}<br>
<b>Total Trips:</b> {{ doc.total_trips or '' }}<br>
<b>Incoterm:</b> {{ doc.incoterm or '' }}</p>

{% if doc.package_details %}
<h4>Package Details</h4>
<table class="table table-bordered">
  <tr><th>Package</th><th>Specification</th><th>Capacity</th><th>Load Capacity</th><th>Qty</th><th>Remarks</th></tr>
  {% for r in doc.package_details %}
  <tr>
    <td>{{ r.package_type or '' }}</td>
    <td>{{ r.specification or '' }}</td>
    <td>{{ r.capacity or '' }} {{ r.capacity_uom or '' }}</td>
    <td>{{ r.load_capacity or '' }} {{ r.load_capacity_uom or '' }}</td>
    <td>{{ r.qty or '' }}</td>
    <td>{{ r.remarks or '' }}</td>
  </tr>
  {% endfor %}
</table>
{% endif %}

{% if doc.route_legs %}
<h4>Route Legs</h4>
<table class="table table-bordered">
  <tr><th>No</th><th>Leg</th><th>Role</th><th>Location</th><th>City</th><th>Province</th><th>Mode</th></tr>
  {% for r in doc.route_legs|sort(attribute='sequence') %}
  <tr>
    <td>{{ r.sequence or loop.index }}</td>
    <td>{{ r.leg_type or '' }}</td>
    <td>{{ r.location_role or '' }}</td>
    <td>{{ r.location_name or '' }}</td>
    <td>{{ r.city or '' }}</td>
    <td>{{ r.province or '' }}</td>
    <td>{{ r.transport_mode or '' }}</td>
  </tr>
  {% endfor %}
</table>
{% endif %}

{% if doc.service_attributes %}
<h4>Service Attributes</h4>
<table class="table table-bordered">
  {% for r in doc.service_attributes|sort(attribute='print_sequence') if r.show_in_print %}
  <tr><td><b>{{ r.attribute_label }}</b></td><td>{{ r.attribute_value or '' }} {{ r.attribute_uom or '' }}</td></tr>
  {% endfor %}
</table>
{% endif %}

<h4>Items</h4>
<table class="table table-bordered">
  <tr><th>Description</th><th>Qty</th><th>UOM</th><th>Rate</th><th>Amount</th></tr>
  {% for r in doc.items %}
  <tr>
    <td>{{ r.item_name or r.description }}</td>
    <td>{{ r.qty }}</td>
    <td>{{ r.uom }}</td>
    <td class="text-right">{{ frappe.format(r.rate, {'fieldtype':'Currency', 'options': doc.currency}) }}</td>
    <td class="text-right">{{ frappe.format(r.amount, {'fieldtype':'Currency', 'options': doc.currency}) }}</td>
  </tr>
  {% endfor %}
</table>
<p class="text-right">
  <b>Total before VAT:</b> {{ frappe.format(doc.net_total, {'fieldtype':'Currency', 'options': doc.currency}) }}<br>
  {% for tax in doc.taxes %}
  <b>{{ tax.description or tax.account_head or 'Tax' }}:</b> {{ frappe.format(tax.tax_amount, {'fieldtype':'Currency', 'options': doc.currency}) }}<br>
  {% endfor %}
  <b>Grand Total:</b> {{ frappe.format(doc.grand_total, {'fieldtype':'Currency', 'options': doc.currency}) }}
</p>

{% set includes = doc.service_scopes|selectattr('scope_type','equalto','Include')|list %}
{% if includes %}
<h4>Includes</h4>
<ul>{% for r in includes|sort(attribute='print_sequence') %}<li>{{ r.description }}{% if r.condition %} — {{ r.condition }}{% endif %}</li>{% endfor %}</ul>
{% endif %}

{% set excludes = doc.service_scopes|selectattr('scope_type','equalto','Exclude')|list %}
{% if excludes %}
<h4>Excludes</h4>
<ul>{% for r in excludes|sort(attribute='print_sequence') %}<li>{{ r.description }}{% if r.condition %} — {{ r.condition }}{% endif %}</li>{% endfor %}</ul>
{% endif %}

{% if doc.additional_charges %}
<h4>Additional Charges</h4>
<table class="table table-bordered">
  <tr><th>Type</th><th>Description</th><th>Rate</th><th>UOM</th><th>Condition</th></tr>
  {% for r in doc.additional_charges|sort(attribute='print_sequence') %}
  <tr>
    <td>{{ r.charge_type or '' }}</td>
    <td>{{ r.description or '' }}</td>
    <td>{{ frappe.format(r.rate, {'fieldtype':'Currency', 'options': doc.currency}) if r.rate else '' }}</td>
    <td>{{ r.uom or '' }}</td>
    <td>{{ r.condition or '' }}</td>
  </tr>
  {% endfor %}
</table>
{% endif %}

{% if doc.terms %}<h4>Terms and Conditions</h4><div>{{ doc.terms }}</div>{% endif %}
{% if doc.logistics_remarks %}<h4>Remarks</h4><p>{{ doc.logistics_remarks }}</p>{% endif %}

<br><br>
<table style="width:100%">
  <tr><td>Prepared By</td><td class="text-right">Approved By / Customer</td></tr>
  <tr><td style="height:80px"></td><td></td></tr>
  <tr><td>____________________</td><td class="text-right">____________________</td></tr>
</table>
"""


def make_field(fieldname, label, fieldtype, **kwargs):
    data = {"fieldname": fieldname, "label": label, "fieldtype": fieldtype}
    data.update(kwargs)
    return data


def ensure_module():
    if not frappe.db.exists("Module Def", "Logistics"):
        frappe.get_doc({
            "doctype": "Module Def",
            "module_name": "Logistics",
            "app_name": "oakglobal_erp_custom",
            "custom": 0,
        }).insert(ignore_permissions=True)


def ensure_doctype(name, fields, istable=False, autoname=None):
    if frappe.db.exists("DocType", name):
        return
    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": name,
        "module": "Logistics",
        "custom": 1,
        "istable": 1 if istable else 0,
        "editable_grid": 1 if istable else 0,
        "autoname": autoname or ("field:service_name" if name == "Job Service Type" else ""),
        "engine": "InnoDB",
        "fields": fields,
        "permissions": [] if istable else [{
            "role": "System Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
        }],
    })
    doc.insert(ignore_permissions=True)


def create_doctypes():
    ensure_module()
    ensure_doctype("Job Service Type", [
        make_field("service_code", "Service Code", "Data", reqd=1, unique=1, in_list_view=1),
        make_field("service_name", "Service Name", "Data", reqd=1, in_list_view=1),
        make_field("default_transport_mode", "Default Transport Mode", "Select", options=TRANSPORT_MODES),
        make_field("default_item_group", "Default Item Group", "Link", options="Item Group"),
        make_field("default_uom", "Default UOM", "Link", options="UOM"),
        make_field("default_terms_template", "Default Terms Template", "Link", options="Terms and Conditions"),
        make_field("default_print_format", "Default Print Format", "Data"),
        make_field("requires_route", "Requires Route", "Check"),
        make_field("requires_package_detail", "Requires Package Detail", "Check"),
        make_field("requires_trip_count", "Requires Trip Count", "Check"),
        make_field("is_active", "Is Active", "Check", default=1),
    ])
    ensure_doctype("Quotation Package Detail", [
        make_field("package_type", "Package Type", "Data", in_list_view=1),
        make_field("specification", "Specification", "Data"),
        make_field("capacity", "Capacity", "Float"),
        make_field("capacity_uom", "Capacity UOM", "Link", options="UOM"),
        make_field("load_capacity", "Load Capacity", "Float"),
        make_field("load_capacity_uom", "Load Capacity UOM", "Link", options="UOM"),
        make_field("qty", "Qty", "Float"),
        make_field("remarks", "Remarks", "Small Text"),
    ], istable=True)
    ensure_doctype("Quotation Route Leg", [
        make_field("sequence", "Sequence", "Int", in_list_view=1),
        make_field("leg_type", "Leg Type", "Select", options=LEG_TYPES, in_list_view=1),
        make_field("location_role", "Location Role", "Select", options=LOCATION_ROLES, in_list_view=1),
        make_field("location_name", "Location Name", "Data", in_list_view=1),
        make_field("city", "City", "Data"),
        make_field("province", "Province", "Data"),
        make_field("transport_mode", "Transport Mode", "Select", options="Trucking\nSea Freight\nAir Freight\nMultimodal\nOther"),
        make_field("remarks", "Remarks", "Small Text"),
    ], istable=True)
    ensure_doctype("Quotation Service Scope", [
        make_field("scope_type", "Scope Type", "Select", options="Include\nExclude", reqd=1, in_list_view=1),
        make_field("description", "Description", "Small Text", reqd=1, in_list_view=1),
        make_field("chargeable", "Chargeable", "Check"),
        make_field("amount", "Amount", "Currency"),
        make_field("condition", "Condition", "Small Text"),
        make_field("print_sequence", "Print Sequence", "Int"),
    ], istable=True)
    ensure_doctype("Quotation Additional Charge", [
        make_field("charge_type", "Charge Type", "Select", options=CHARGE_TYPES, in_list_view=1),
        make_field("description", "Description", "Small Text", in_list_view=1),
        make_field("rate", "Rate", "Currency"),
        make_field("uom", "UOM", "Data"),
        make_field("condition", "Condition", "Small Text"),
        make_field("included_in_total", "Included in Total", "Check"),
        make_field("taxable", "Taxable", "Check"),
        make_field("print_sequence", "Print Sequence", "Int"),
    ], istable=True)
    ensure_doctype("Quotation Service Attribute", [
        make_field("attribute_label", "Attribute Label", "Data", reqd=1, in_list_view=1),
        make_field("attribute_value", "Attribute Value", "Data", in_list_view=1),
        make_field("attribute_uom", "Attribute UOM", "Data"),
        make_field("print_sequence", "Print Sequence", "Int"),
        make_field("show_in_print", "Show in Print", "Check", default=1),
    ], istable=True)


def create_quotation_fields():
    create_custom_fields({
        "Quotation": [
            {"fieldname": "logistics_service_section", "label": "Logistics Service", "fieldtype": "Section Break", "insert_after": "order_type", "collapsible": 1},
            {"fieldname": "job_service_type", "label": "Job Service Type", "fieldtype": "Link", "options": "Job Service Type", "reqd": 1},
            {"fieldname": "job_service_title", "label": "Job Service Title", "fieldtype": "Data"},
            {"fieldname": "logistics_col_break_1", "fieldtype": "Column Break"},
            {"fieldname": "commodity", "label": "Commodity", "fieldtype": "Data"},
            {"fieldname": "total_quantity", "label": "Total Quantity", "fieldtype": "Float"},
            {"fieldname": "quantity_uom", "label": "Quantity UOM", "fieldtype": "Link", "options": "UOM"},
            {"fieldname": "logistics_col_break_2", "fieldtype": "Column Break"},
            {"fieldname": "total_trips", "label": "Total Trips", "fieldtype": "Int"},
            {"fieldname": "logistics_remarks", "label": "Logistics Remarks", "fieldtype": "Small Text"},
            {"fieldname": "package_details_section", "label": "Package Details", "fieldtype": "Section Break", "insert_after": "logistics_remarks", "collapsible": 1},
            {"fieldname": "package_details", "label": "Package Details", "fieldtype": "Table", "options": "Quotation Package Detail"},
            {"fieldname": "route_legs_section", "label": "Route Legs", "fieldtype": "Section Break", "insert_after": "package_details", "collapsible": 1},
            {"fieldname": "route_legs", "label": "Route Legs", "fieldtype": "Table", "options": "Quotation Route Leg"},
            {"fieldname": "service_scope_section", "label": "Service Scope", "fieldtype": "Section Break", "insert_after": "route_legs", "collapsible": 1},
            {"fieldname": "service_scopes", "label": "Service Scope", "fieldtype": "Table", "options": "Quotation Service Scope"},
            {"fieldname": "additional_charges_section", "label": "Additional Charges", "fieldtype": "Section Break", "insert_after": "service_scopes", "collapsible": 1},
            {"fieldname": "additional_charges", "label": "Additional Charges", "fieldtype": "Table", "options": "Quotation Additional Charge"},
            {"fieldname": "service_attributes_section", "label": "Service Attributes", "fieldtype": "Section Break", "insert_after": "additional_charges", "collapsible": 1},
            {"fieldname": "service_attributes", "label": "Service Attributes", "fieldtype": "Table", "options": "Quotation Service Attribute"},
        ]
    }, update=True)


def create_records():
    for code, name, mode, req_route, req_pkg, req_trip in SERVICE_TYPES:
        if not frappe.db.exists("Job Service Type", name):
            frappe.get_doc({
                "doctype": "Job Service Type",
                "service_code": code,
                "service_name": name,
                "default_transport_mode": mode,
                "requires_route": req_route,
                "requires_package_detail": req_pkg,
                "requires_trip_count": req_trip,
                "is_active": 1,
            }).insert(ignore_permissions=True)
    if not frappe.db.exists("Terms and Conditions", "Door to Door Transport Terms"):
        frappe.get_doc({
            "doctype": "Terms and Conditions",
            "title": "Door to Door Transport Terms",
            "terms": "<ol><li>All prices quoted are before VAT 11%.</li><li>Overtime charge IDR 1,500,000 per 12 hours applies if loading/unloading exceeds 12 hours.</li><li>Incoterm DDP (Delivered Duty Paid) — door-to-door.</li><li>Payment Term: 14 days after invoice received.</li><li>Validity follows Quotation Valid Till date.</li><li>Rate is subject to government regulation, BBM increment, toll fee, and sea freight rate adjustment.</li><li>Rate may be reviewed in case of significant changes in fuel price or shipping cost.</li></ol>",
        }).insert(ignore_permissions=True)
    dtd = frappe.get_doc("Job Service Type", "Door to Door")
    dtd.default_terms_template = "Door to Door Transport Terms"
    dtd.default_print_format = "Logistics Quotation"
    dtd.save(ignore_permissions=True)


def create_client_script():
    script = r"""
frappe.ui.form.on('Quotation', {
  job_service_type(frm) {
    if (!frm.doc.job_service_type) return;
    frappe.db.get_doc('Job Service Type', frm.doc.job_service_type).then(service => {
      if (!frm.doc.job_service_title) {
        frm.set_value('job_service_title', service.service_name);
      }
      if (service.default_terms_template) {
        frm.set_value('tc_name', service.default_terms_template);
      }
      frm.toggle_display('route_legs_section', !!service.requires_route || (frm.doc.route_legs || []).length > 0);
      frm.toggle_display('package_details_section', !!service.requires_package_detail || (frm.doc.package_details || []).length > 0);
    });
  },
  refresh(frm) {
    frm.trigger('job_service_type');
  },
  total_trips(frm) {
    if (frm.doc.total_trips && (frm.doc.items || []).length === 1 && !frm.doc.items[0].qty) {
      frappe.model.set_value(frm.doc.items[0].doctype, frm.doc.items[0].name, 'qty', frm.doc.total_trips);
    }
  }
});
"""
    if frappe.db.exists("Client Script", "Quotation Logistics"):
        doc = frappe.get_doc("Client Script", "Quotation Logistics")
        doc.script = script
        doc.enabled = 1
        doc.save(ignore_permissions=True)
    else:
        frappe.get_doc({
            "doctype": "Client Script",
            "name": "Quotation Logistics",
            "dt": "Quotation",
            "view": "Form",
            "enabled": 1,
            "script": script,
        }).insert(ignore_permissions=True)


def create_print_format():
    data = {
        "doctype": "Print Format",
        "name": "Logistics Quotation",
        "doc_type": "Quotation",
        "print_format_type": "Jinja",
        "html": LOGISTICS_PRINT_HTML,
        "standard": "No",
        "custom_format": 1,
        "disabled": 0,
    }
    if frappe.db.exists("Print Format", "Logistics Quotation"):
        doc = frappe.get_doc("Print Format", "Logistics Quotation")
        doc.update(data)
        doc.save(ignore_permissions=True)
    else:
        frappe.get_doc(data).insert(ignore_permissions=True)


def run():
    ensure_module()
    create_doctypes()
    create_quotation_fields()
    create_records()
    create_client_script()
    create_print_format()
    frappe.db.commit()


if __name__ == "__main__":
    run()
