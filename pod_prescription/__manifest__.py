
{
    "name": "Pod Prescription",
    "summary": "Pod prescription base",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Medical",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": [
        "pod_administration",
        "pod_terminology_sct",
        "product",
        "stock",
    ],
    "data": [
        "security/pod_security.xml",
        "data/sct_data.xml",
        "views/pod_menu.xml",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": ["demo/sct_data.xml", "demo/is_medical_device.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
