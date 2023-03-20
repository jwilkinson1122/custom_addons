# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_patient_prescription(models.Model):
    _name = 'podiatry.patient.prescription'
    _description = 'podiatry patient prescription'
    _rec_name = 'product_id'

    @api.depends('product_id')
    def onchange_product(self):
        for each in self:
            if each:
                self.qty_available = self.product_id.qty_available
                self.price = self.product_id.lst_price
            else:
                self.qty_available = 0
                self.price = 0.0

    product_id = fields.Many2one('product.product', 'Name')
    therapeutic_action = fields.Char(
        'Therapeutic effect', help='Therapeutic action')
    price = fields.Float(compute=onchange_product, string='Price', store=True)
    qty_available = fields.Integer(
        compute=onchange_product, string='Quantity Available', store=True)
    indications = fields.Text('Indications')
    active_component = fields.Char(string="Active Component")
    presentation = fields.Text('Presentation')
    composition = fields.Text('Composition')
    adverse_reaction = fields.Text('Adverse Reactions')
    storage = fields.Text('Storage Condition')
    notes = fields.Text('Extra Info')
    treatment = fields.Many2one(
        'podiatry.treatment', string='Treatment', required=True)
    podiatry_patient_prescription_id1 = fields.Many2one(
        'podiatry.patient', string='Device')
    is_active = fields.Boolean(string='Active', default=True)
    start_treatment = fields.Datetime(
        string='Start Of Treatment', required=True)
    course_completed = fields.Boolean(string="Course Completed")
    doctor_practitioner_id = fields.Many2one(
        'podiatry.practitioner', string='Practitioner')
    indication = fields.Many2one('podiatry.pathology', string='Indication')
    end_treatment = fields.Datetime(string='End Of Treatment', required=True)
    discontinued = fields.Boolean(string='Discontinued')
    route = fields.Many2one('podiatry.product.route',
                            string=" Administration Route ")
    quantity = fields.Float(string='Quantity')
    qty = fields.Integer(string='X')
    quantity_unit = fields.Many2one(
        'podiatry.quantity.unit', string='Quantity Unit')
    duration = fields.Integer(string="Treatment Duration")
    duration_period = fields.Selection([('minutes', 'Minutes'),
                                        ('hours', 'hours'),
                                        ('days', 'Days'),
                                        ('months', 'Months'),
                                        ('years', 'Years'),
                                        ('indefine', 'Indefine')], string='Treatment Period')
    common_quantity = fields.Many2one(
        'podiatry.prescription.quantity', string='Frequency')
    admin_times = fields.Char(string='Admin Hours')
    frequency = fields.Integer(string='Frequency')
    frequency_unit = fields.Selection([('seconds', 'Seconds'),
                                       ('minutes', 'Minutes'),
                                       ('hours', 'hours'),
                                       ('days', 'Days'),
                                       ('weeks', 'Weeks'),
                                       ('wr', 'When Required')], string='Unit')
    notes = fields.Text(string='Notes')
    podiatry_patient_prescription_id = fields.Many2one(
        'podiatry.patient', 'Patient')
