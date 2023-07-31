# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Partner Medical Medication",
    "summary": "Add a medication button to the partner form view",
    "version": "13.0.0.0.0",
    "category": "Medical",
    "website": "https://laslabs.com/",
    "author": "LasLabs",
    "license": "GPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "medical_medication",
    ],
    "data": [
        "views/res_partner_view.xml",
        "views/medical_patient_medication_view.xml",
    ],
}
