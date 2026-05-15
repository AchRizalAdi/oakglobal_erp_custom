app_name = "oakglobal_erp_custom"
app_title = "Oakglobal ERP Custom"
app_publisher = "Oakglobal Maritim"
app_description = "Custom ERPNext app for Oakglobal Maritim"
app_email = "admin@oakglobalmaritim.com"
app_license = "MIT"

# Website assets. Keep ERPNext core untouched.
# web_include_css = [
#     "/assets/oakglobal_erp_custom/css/oakglobal_login.css",
# ]

# Fixtures can be added later to version-control UI customizations.
fixtures = [
    {"doctype": "DocType", "filters": [["name", "in", ["Job Service Type", "Quotation Package Detail", "Quotation Route Leg", "Quotation Service Scope", "Quotation Additional Charge", "Quotation Service Attribute"]]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Quotation"]]},
    {"doctype": "Client Script", "filters": [["name", "=", "Quotation Logistics"]]},
    {"doctype": "Print Format", "filters": [["name", "=", "Logistics Quotation"]]},
    {"doctype": "Terms and Conditions", "filters": [["title", "=", "Door to Door Transport Terms"]]},
    {"doctype": "Job Service Type", "filters": [["service_code", "in", ["DTD", "PTP", "DTP", "PTD", "TRK", "SEA", "CCL", "WHS", "ISO"]]]},
]

doc_events = {
    "Quotation": {
        "validate": "oakglobal_erp_custom.logistics.quotation_hooks.validate_quotation"
    }
}

