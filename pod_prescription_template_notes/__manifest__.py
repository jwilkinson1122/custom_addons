{
    "name": "NWPL - Prescription Order Template Notes",
    "summary": """
        Set notes on prescription order templates.
    """,
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "category": "Podiatry/Prescription",
    "version": "17.0.0.0.0",
    "license": "LGPL-3",
    "depends": [
        "pod_prescription_management", 
        "pod_prescription_notes"],
    "data": ["views/prescription_order_template_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": ["description/icon.png"],
}
