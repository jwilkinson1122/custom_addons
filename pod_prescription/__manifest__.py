{
    "name": "Podiatry Prescription",
    "summary": "Podiatry prescription base",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
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
    "demo": [
        "demo/sct_data.xml", 
        "demo/prescription.xml"
        ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
