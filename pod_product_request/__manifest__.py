
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Request",
    "summary": """
        This addon sets the base of the pod fhir concepts
        of device.request and device.request""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": [
        "pod_administration_encounter",
        "mail",
        "pod_base",
        "web_domain_field",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/pod_patient.xml",
        "views/pod_encounter.xml",
        "data/ir_sequence_data.xml",
        "views/pod_product_template.xml",
        "views/pod_product_product.xml",
        "views/pod_product_administration.xml",
        "views/pod_product_request_order.xml",
        "views/pod_product_request.xml",
        "views/device_form.xml",
        "views/pod_administration_route.xml",
    ],
    "demo": ["demo/pod_product_request_demo.xml"],
}
