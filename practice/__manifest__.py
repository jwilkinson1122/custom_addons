# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Practice",
    "version": "14.0.1.1.0",
    "license": "AGPL-3",
    "summary": "Manage practices information",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/partner-contact",
    "depends": ["mail"],
    "data": [
        "data/ir.module.category.csv",
        "data/practice.species.csv",
        "data/practice.breed.csv",
        "data/practice.color.csv",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/practice_color.xml",
        "views/practice_breed.xml",
        "views/practice_species.xml",
        "views/practice.xml",
        "views/menu.xml",
    ],
    "application": True,
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
