# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Manufacturer",
    "summary": "Extension of medical with concept of medical manufacturers.",
    "version": "13.0.0.0.0",
    "category": "Medical",
    "website": "https://laslabs.com",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "GPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "medical_medicament",
    ],
    "data": [
        "views/medical_manufacturer_view.xml",
        "views/medical_menu.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/medical_manufacturer_demo.xml",
    ],
}
