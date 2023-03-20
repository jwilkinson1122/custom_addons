# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_prescription_line(models.Model):
    _name = "podiatry.prescription.line"
    _description = 'podiatry prescription line'
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


    name = fields.Many2one('podiatry.prescription.order', 'Prescription ID')
    treatment_id = fields.Many2one('podiatry.treatment', 'Treatment')
    product_id = fields.Many2one('product.product', 'Name')
    therapeutic_action = fields.Char(
        'Therapeutic effect', help='Therapeutic action')
    indication = fields.Text('Indications')
    active_component = fields.Char(string="Active Component")
    presentation = fields.Text('Presentation')
    composition = fields.Text('Composition')
    quantity = fields.Text('Quantity')
    adverse_reaction = fields.Text('Adverse Reactions')
    storage = fields.Text('Storage Condition')
    notes = fields.Text('Extra Info')
    allow_substitution = fields.Boolean('Allow Substitution')
    form = fields.Char('Form')
    prnt = fields.Boolean('Print')
    route = fields.Char('Administration Route')
    end_treatement = fields.Datetime('Administration Route')
    quantity = fields.Float('Quantity')
    quantity_unit_id = fields.Many2one(
        'podiatry.quantity.unit', 'Quantity Unit')
    qty = fields.Integer('x')
    prescription_quantity_id = fields.Many2one(
        'podiatry.prescription.quantity', 'Frequency')
    price = fields.Float(compute=onchange_product, string='Price', store=True)
    qty_available = fields.Integer(
        compute=onchange_product, string='Quantity Available', store=True)
    admin_times = fields.Char('Admin Hours', size=128)
    frequency = fields.Integer('Frequency')
    frequency_unit = fields.Selection([('seconds', 'Seconds'), ('minutes', 'Minutes'), (
        'hours', 'hours'), ('days', 'Days'), ('weeks', 'Weeks'), ('wr', 'When Required')], 'Unit')
    duration = fields.Integer('Treatment Duration')
    duration_period = fields.Selection([('minutes', 'Minutes'), ('hours', 'hours'), ('days', 'Days'), (
        'months', 'Months'), ('years', 'Years'), ('indefine', 'Indefine')], 'Treatment Period')
    review = fields.Datetime('Review')
    refills = fields.Integer('Refills#')
    short_comment = fields.Char('Comment', size=128)
    end_treatment = fields.Datetime('End of treatment')
    start_treatment = fields.Datetime('Start of treatment')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
