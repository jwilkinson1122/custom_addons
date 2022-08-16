# Copyright 2016 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import api, SUPERUSER_ID


def _update_medicament_type(cr, registry):
    with cr.savepoint():
        cr.execute(
            """UPDATE product_template SET type = 'product'
            WHERE is_medicament = TRUE"""
        )

    with cr.savepoint():
        env = api.Environment(cr, SUPERUSER_ID, {})
        medication_model = env['medical.patient.medication']
        medications = medication_model.search([])
        for medication in medications:
            medication.onchange_template_id()
