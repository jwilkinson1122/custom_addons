# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PatientPrescriptions(models.Model):
    _name = 'patient.prescriptions'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Patient Prescriptions'

    partner_id = fields.Many2one('res.partner', string='Patient')
    name = fields.Char(string="Name", )
    registration_no = fields.Char(string="Registration No")
    disease_type_id = fields.Many2one('disease.type', string='Disease Type',
                                      tracking=True, required=True)
    disease_stage_id = fields.Many2one('disease.stage', string='Disease Stage',
                                       tracking=True)
    date = fields.Datetime(string='Date')
    partner_id = fields.Many2one('res.partner', string='Doctor')
    remark = fields.Text(string='Remark')
    line_ids = fields.One2many('patient.prescriptions.line', 'prescriptions_id', string="Lines")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('patient.prescriptions') or 'New'
        return super(PatientPrescriptions, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            rec.registration_no = rec.partner_id.registration_no
            # rec.disease_type_id = rec.partner_id.disease_type_id
            # rec.disease_stage_id = rec.partner_id.disease_stage_id


class PatientPrescriptionsLine(models.Model):
    _name = 'patient.prescriptions.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'prescriptions_id'
    _description = 'Patient Prescriptions Line'

    prescriptions_id = fields.Many2one('patient.prescriptions', string='Prescription')
    product_id = fields.Many2one('product.product', string='Medicine')
    uom_id = fields.Many2one('uom.uom', string='Unit')
    quantity = fields.Float(string="Quantity")
    dose = fields.Float(string="Dose")
    dose_unit = fields.Char(string="Dose Unit")
    morning = fields.Boolean(string="Morning")
    afternoon = fields.Boolean(string="Afternoon")
    evening = fields.Boolean(string="Evening")
    night = fields.Boolean(string="Night")
    when_take = fields.Selection([('after', 'After Eat'), ('before', 'Before Eat')])
    remark = fields.Text(string='Remark')
