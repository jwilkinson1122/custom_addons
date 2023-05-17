# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PatientPrescriptions(models.Model):
    _name = 'patient.prescriptions'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Patient Prescriptions'
    
    doctor_id = fields.Many2one("res.partner", domain=[('is_doctor','=',True)], string="Doctor", index=True, tracking=True)
    patient_id = fields.Many2one("res.partner", domain=[('is_patient','=',True)], string="Patient", index=True, tracking=True)
    practice_id = fields.Many2one("res.partner", domain=[('is_clinic','=',True)], string="Clinic", index=True, tracking=True)
    name = fields.Char(string="Name", )
    registration_no = fields.Char(string="Registration No")
    disease_type_id = fields.Many2one('condition.type', string='Condition Type',
                                      tracking=True, required=True)
    disease_stage_id = fields.Many2one('condition.stage', string='Condition Stage',
                                       tracking=True)
    date = fields.Datetime(string='Date')
    remark = fields.Text(string='Remark')
    line_ids = fields.One2many('patient.prescriptions.line', 'prescriptions_id', string="Lines")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('patient.prescriptions') or 'New'
        return super(PatientPrescriptions, self).create(vals)

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        for rec in self:
            rec.registration_no = rec.patient_id.registration_no
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
