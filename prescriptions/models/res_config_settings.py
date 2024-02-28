# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    deletion_delay = fields.Integer(config_parameter="prescriptions.deletion_delay", default=30,
                                    help='Delay after permanent deletion of the prescription in the trash (days)')

    _sql_constraints = [
        ('check_deletion_delay', 'CHECK(deletion_delay >= 0)', 'The deletion delay should be positive.'),
    ]
