# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Patient Species",
    "summary": "Adds pet concept to medical_patient",
    "version": "13.0.0.0.0",
    "category": "Medical",
    "website": "https://laslabs.com/",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "maintainer": "LasLabs, Odoo Community Association (OCA)",
    "license": "GPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "medical",
    ],
    "data": [
        'data/medical_patient_species.xml',
        'security/ir.model.access.csv',
        'views/medical_patient_species_view.xml',
        'views/medical_patient_view.xml',
    ],
    "post_init_hook": "post_init_hook",
}
