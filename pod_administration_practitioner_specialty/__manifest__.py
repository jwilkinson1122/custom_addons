
{
    "name": "Podiatry Administration Practitioner Specialty",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatiric.com",
    "license": "LGPL-3",
    "depends": [
        "pod_administration_practitioner",
        "pod_terminology_sct",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sct_data.xml",
        "data/pod_role.xml",
        "views/res_partner_views.xml",
        "views/pod_specialty.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
