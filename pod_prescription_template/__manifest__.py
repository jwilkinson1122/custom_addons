{
    "name": "NWPL - Prescription Order Template",
    "summary": """
        Setup prescription order template.
    """,
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "category": "Podiatry/Prescription",
    "version": "17.0.0.0.0",
    "license": "LGPL-3",
    "depends": [
        "pod_prescription_notes", 
        "pod_prescription_template_notes"
        ],
    "data": ["views/prescription_order_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": ["description/icon.png"],
}
