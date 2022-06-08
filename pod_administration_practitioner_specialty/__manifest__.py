

{
    "name": "Pod Administration Practitioner Specialty",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Medical",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": [
        "pod_administration_practitioner",
        "pod_terminology_sct",
    ],
    "data": [
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "data/sct_data.xml",
        "views/res_partner_views.xml",
        "views/pod_specialty.xml",
    ],
    "demo": [""],
    "installable": True,
    "application": False,
    "auto_install": False,
}
