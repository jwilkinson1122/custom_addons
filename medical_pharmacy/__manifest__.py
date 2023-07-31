# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Pharmacy",
    "summary": "Adds pharmacy namespace on partners.",
    "version": "13.0.0.0.0",
    "category": "Medical",
    "website": "https://laslabs.com",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "GPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "medical_center",
        "medical_physician",
    ],
    "data": [
        "views/medical_pharmacy_view.xml",
        "views/medical_pharmacist_view.xml",
        "views/medical_menu.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/medical_pharmacy_demo.xml",
        "demo/medical_pharmacist_demo.xml",
    ],
}
