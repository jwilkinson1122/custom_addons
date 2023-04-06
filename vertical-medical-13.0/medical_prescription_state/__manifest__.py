# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Prescription Order States",
    "version": "13.0.0.0.0",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "category": "Medical",
    "website": "https://laslabs.com",
    "license": "GPL-3",
    "post_init_hook": "post_init_hook",
    "depends": [
        "base_kanban_stage",
        "medical_prescription",
    ],
    "data": [
        "views/medical_prescription_order.xml",
        "views/medical_prescription_order_line.xml",
        "data/base_kanban_stage.xml",
    ],
    "installable": True,
    "auto_install": False,
}
