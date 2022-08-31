

{
    "name": "Podiatry Prescription",
    "summary": "Podiatry prescription base",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": [
        "podiatry_administration",
        "podiatry_terminology_sct",
        "product",
        "stock",
    ],
    "data": [
        "security/podiatry_security.xml",
        "data/sct_data.xml",
        "views/podiatry_menu.xml",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": ["demo/sct_data.xml", "demo/device.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
