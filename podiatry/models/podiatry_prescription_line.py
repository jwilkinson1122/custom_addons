# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime


class PrescriptionLine(models.Model):
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

    name = fields.Many2one('podiatry.prescription', 'Prescription ID')
    prescription_id = fields.Many2one("podiatry.prescription", required=True)
    patient_id = fields.Many2one("podiatry.patient", required=True)
    product_id = fields.Many2one('product.product', 'Name')

    # right_photo = fields.Image("Right Photo")
    # left_photo = fields.Image("Left Photo")
    # left_obj_model = fields.Binary("Left Obj")
    # left_obj_file_name = fields.Char(string="Left Obj File Name")
    # right_obj_model = fields.Binary("Right Obj")
    # right_obj_file_name = fields.Char(string="Right Obj File Name")
    # right_photo = fields.Binary(related="patient_id.right_photo")
    # left_photo = fields.Binary(related="patient_id.left_photo")
    patient_left_photo = fields.Binary(related="patient_id.left_photo")
    patient_right_photo = fields.Binary(related="patient_id.right_photo")

    price = fields.Float(compute=onchange_product, string='Price', store=True)
    qty_available = fields.Integer(
        compute=onchange_product, string='Quantity Available', store=True)
    pathologies = fields.Text('Pathologies')
    pathology = fields.Char('Pathology')
    laterality = fields.Selection(
        [('left', 'Left Only'), ('right', 'Right Only'), ('bilateral', 'Bilateral')], help="""" """)
    notes = fields.Text('Extra Info')
    allow_substitution = fields.Boolean('Allow Substitution')
    form = fields.Char('Form')
    prnt = fields.Boolean('Print')
    quantity = fields.Float('Quantity')
    quantity_unit_id = fields.Many2one(
        'podiatry.quantity.unit', 'Quantity Unit')
    qty = fields.Integer('x')
    device_quantity_id = fields.Many2one(
        'podiatry.device.quantity', 'Quantity')
    quantity = fields.Integer('Quantity')
    short_comment = fields.Char('Comment', size=128)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
