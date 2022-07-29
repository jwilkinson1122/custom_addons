# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Device",
    "version": "15.0.1.0.1",
    "license": "AGPL-3",
    "summary": "Manage devices information",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/partner-contact",
    "depends": ["mail"],
    "data": [
        "data/ir.module.category.csv",
        "data/device.category.csv",
        "data/device.type.csv",
        "data/device.color.csv",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/device_color.xml",
        "views/device_type.xml",
        "views/device_category.xml",
        "views/device.xml",
        "views/menu.xml",
    ],
    "application": True,
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
