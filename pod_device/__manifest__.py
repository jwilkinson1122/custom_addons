# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Device",
    "summary": "Podiatry device base",
    "version": "15.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "category": "Podiatry",
    "website": "https://github.com/tegin/pod-fhir",
    "license": "LGPL-3",
    "depends": [
        "pod_base",
        "pod_terminology_sct",
        "pod_terminology_atc",
        "product",
        "stock",
    ],
    "data": [
        "data/sct_data.xml",
        "views/pod_menu.xml",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": ["demo/sct_data.xml", "demo/device.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
