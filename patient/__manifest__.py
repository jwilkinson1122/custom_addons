# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Patient",
    "version": "14.0.1.2.0",
    "license": "AGPL-3",
    "summary": "Manage patients information",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/partner-contact",
    "depends": ["mail"],
    "data": [
        "data/ir.module.category.csv",
        "data/patient.species.csv",
        "data/patient.breed.csv",
        "data/patient.color.csv",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/patient_color.xml",
        "views/patient_breed.xml",
        "views/patient_species.xml",
        "views/patient.xml",
        "views/menu.xml",
    ],
    "application": True,
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
