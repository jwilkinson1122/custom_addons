# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Patient",
    "version": "14.0.1.1.0",
    "license": "AGPL-3",
    "summary": "Manage patients information",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/partner-contact",
    "depends": ["mail"],
    "data": [
        "data/ir.module.category.csv",
        "data/patient.devicecat.csv",
        "data/patient.devicegroup.csv",
        "data/patient.devicetype.csv",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/patient_devicetype.xml",
        "views/patient_devicegroup.xml",
        "views/patient_devicecat.xml",
        "views/patient.xml",
        "views/menu.xml",
    ],
    "application": True,
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
