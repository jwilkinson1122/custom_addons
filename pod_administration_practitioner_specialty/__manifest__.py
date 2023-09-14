# Copyright 2017 LasLabs Inc.
# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Administration Practitioner Specialty",
    "version": "15.0.1.0.0",
    "author": "ForgeFlow, CreuBlanca, LasLabs, "
    "Odoo Community Association (OCA)",
    "category": "Medical",
    "website": "https://github.com/tegin/medical-fhir",
    "license": "LGPL-3",
    "depends": [
        "medical_administration_practitioner",
        "medical_terminology_sct",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sct_data.xml",
        "views/res_partner_views.xml",
        "views/medical_specialty.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
