# Copyright 2017 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html)

from odoo import api, fields, models


class MedicalPharmacy(models.Model):
    _inherit = 'medical.pharmacy'

    is_verified = fields.Boolean(
        string='Verified',
        help='Is this pharmacy a verified entity?'
    )
    verified_by_id = fields.Many2one(
        string='Verified By',
        comodel_name='res.users',
        store=True,
        compute='_compute_verified_by_id_and_date',
    )
    verified_date = fields.Datetime(
        store=True,
        compute='_compute_verified_by_id_and_date',
    )

    @api.depends('is_verified')
    def _compute_verified_by_id_and_date(self):
        for rec_id in self:
            if rec_id.is_verified and not rec_id.verified_date:
                rec_id.verified_by_id = self.env.user.id
                rec_id.verified_date = fields.Datetime.now()
