

{
    "name": "Podiatry Administration Practitioner Specialty",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": [
        "podiatry_administration_practitioner",
        "podiatry_terminology_sct",
    ],
    "data": [
        "security/podiatry_security.xml",
        "security/ir.model.access.csv",
        "data/sct_data.xml",
        "views/res_partner_views.xml",
        "views/podiatry_specialty.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
