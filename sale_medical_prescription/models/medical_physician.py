# Copyright 2017 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html)

from odoo import api, fields, models


class MedicalPhysician(models.Model):
    _inherit = 'medical.physician'

    is_verified = fields.Boolean(
        string='Verified',
        help='Is this doctor a verified entity?',
    )
    verified_by_id = fields.Many2one(
        string='Verified By',
        comodel_name='res.users',
        store=True,
        compute='_compute_verified_by_id_and_date',
    )
    verified_date = fields.Datetime(
        string='Verified Date',
        store=True,
        compute='_compute_verified_by_id_and_date',
    )

    @api.depends('is_verified')
    def _compute_verified_by_id_and_date(self):
        for record in self:
            if record.is_verified and not record.verified_date:
                record.verified_by_id = self.env.user.id
                record.verified_date = fields.Datetime.now()
