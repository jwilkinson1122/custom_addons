

{
    "name": "Podiatry ATC Codification",
    "summary": "Podiatry codification base",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": ["pod_terminology"],
    "data": [
        "security/ir.model.access.csv",
        "data/atc_data.xml",
        "views/pod_atc_concept_views.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
