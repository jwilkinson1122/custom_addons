{
    "name": "NWPL - Prescription Order Notes",
    "summary": """
        Notes for prescription orders.
    """,
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "category": "Podiatry/Prescription",
    "version": "17.0.0.0.0",
    "license": "LGPL-3",
    "depends": [
        # "sale", 
        "pod_prescription"
        ],
    "data": ["views/prescription_order_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": ["description/icon.png"],
}
