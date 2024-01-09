from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'

    managed_partner_ids = fields.One2many(comodel_name='prescriptions.partner',
                                     inverse_name='parent_id')
    personnel_ids = fields.One2many(comodel_name='prescriptions.partner.personnel',
                                inverse_name='prescriptions_partner_id')
    partner_personnel_rel_ids = fields.One2many(comodel_name='prescriptions.partner.personnel',
                                         inverse_name='partner_id',
                                         string='Partners Served',
                                         help='The partners this person works for.')
    partners_served_ids = fields.One2many(comodel_name='prescriptions.partner', compute='_compute_partners_served')
    patient_ids = fields.One2many(comodel_name='prescriptions.patient', inverse_name='partner_id')

    def write(self, vals):
        if self.patient_ids and 'name' in vals:
            raise ValidationError(_("To change a patient's name, change it from the patient form."))
        return super().write(vals)

    @api.depends('partner_personnel_rel_ids.prescriptions_partner_id')
    def _compute_partners_served(self):
        for rec in self:
            rec.partners_served_ids = rec.partner_personnel_rel_ids.mapped('prescriptions_partner_id')
