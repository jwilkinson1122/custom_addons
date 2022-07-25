from odoo import models, fields, api, _


class Doctor(models.Model):
    _name = "clinic.doctor"
    _description = 'podiatry doctor'
    _inherit = "clinic_patient"

    partner_id = fields.Many2one(
        "res.partner", string="Doctor", index=True, tracking=True
    )

    # _rec_name = 'partner_id'

    # partner_id = fields.Many2one('res.partner', 'Doctor', required=True)
    # clinic_partner_id = fields.Many2one(
    #     'res.partner', domain=[('is_clinic', '=', True)], string='Medical Clinic')
    # code = fields.Char('Id')
    # info = fields.Text('Extra Info')

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')
    active = fields.Boolean(string="Active", default=True)

    # def copy(self, default=None):
    #     if default is None:
    #         default = {}
    #     if not default.get('doctor_name'):
    #         default['doctor_name'] = _("%s (Copy)", self.doctor_name)
    #     default['note'] = "Copied Record"
    #     return super(Doctor, self).copy(default)

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['clinic.prescription'].search_count(
                [('partner_id', '=', rec.id)])
            rec.prescription_count = prescription_count
