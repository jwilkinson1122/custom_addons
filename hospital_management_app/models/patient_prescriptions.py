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
    condition_type_id = fields.Many2one('condition.type', string='Condition Type',
                                      tracking=True, required=True)
    condition_stage_id = fields.Many2one('condition.stage', string='Condition Stage',
                                       tracking=True)
    date = fields.Datetime(string='Date')
    employee_id = fields.Many2one('hr.employee', string='Doctor')
    remark = fields.Text(string='Remark')
    line_ids = fields.One2many('prescription.device.line', 'prescriptions_id', string="Lines")
    option_line_ids = fields.One2many('prescription.option.line', 'prescriptions_id', string="Options")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('patient.prescriptions') or 'New'
        return super(PatientPrescriptions, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            rec.registration_no = rec.partner_id.registration_no
            # rec.condition_type_id = rec.partner_id.condition_type_id
            # rec.condition_stage_id = rec.partner_id.condition_stage_id


class PrescriptionDeviceLine(models.Model):
    _name = 'prescription.device.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'prescriptions_id'
    _description = 'Patient Prescriptions Line'

    prescriptions_id = fields.Many2one('patient.prescriptions', string='Prescription')
    product_id = fields.Many2one('product.product', string='Device')
    uom_id = fields.Many2one('uom.uom', string='Unit')
    quantity = fields.Float(string="Quantity")
    lt_only = fields.Boolean(string="LT")
    rt_only = fields.Boolean(string="RT")
    bl_pair = fields.Boolean(string="BL")
    remark = fields.Text(string='Remark')
    

class PrescriptionOptionsLine(models.Model):
    # _name = 'hospital.patient.registration'
    _name = 'prescription.option.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'prescriptions_id'
    _description = 'Option Order Line'

    prescriptions_id = fields.Many2one('patient.prescriptions', string='Prescription')
    product_id = fields.Many2one('product.product', string='Device')
    uom_id = fields.Many2one('uom.uom', string='Unit')
    quantity = fields.Float(string="Quantity")
    lt_only = fields.Boolean(string="LT")
    rt_only = fields.Boolean(string="RT")
    bl_pair = fields.Boolean(string="BL")
    remark = fields.Text(string='Remark')
    # subtotal = fields.Float(string="Sub Total", compute='compute_subtotal')

    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     for rec in self:
    #         rec.price_unit = rec.product_id.list_price

    # @api.onchange('price_unit', 'quantity')
    # def compute_subtotal(self):
    #     for rec in self:
    #         rec.subtotal = rec.price_unit * rec.quantity

    
 
