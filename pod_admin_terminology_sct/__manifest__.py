

{
    "name": "Podiatry SCT Codification",
    "summary": "Podiatry codification base",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": ["podiatry_terminology"],
    "data": [
        "security/podiatry_security.xml",
        "security/ir.model.access.csv",
        "data/sct_data.xml",
        "views/podiatry_sct_concept_views.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
