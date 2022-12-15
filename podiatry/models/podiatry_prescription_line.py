# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from datetime import date, datetime

_logger = logging.getLogger(__name__)


class PrescriptionLine(models.Model):
    _name = "podiatry.prescription.line"
    _inherit = ['prescription.wizard.mixin']
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

    prescription_id = fields.Many2one(
        comodel_name='podiatry.prescription',
        name="Prescription",
        ondelete='cascade',
        default=lambda self: self._default_prescription_id(),
    )

    name = fields.Many2one('podiatry.prescription', 'Rx ID')
    patient_id = fields.Many2one("podiatry.patient")
    # practice = fields.Char(related='prescription_id.practice_id.name')
    # practitioner = fields.Char(related='prescription_id.practitioner_id.name')
    patient = fields.Char(
        related='prescription_id.patient_id.name', readonly=True,)
    product_id = fields.Many2one('product.product', 'Name')

    field1 = fields.Char()
    field2 = fields.Char()
    field3 = fields.Char()

    @api.model
    def _selection_state(self):
        return [
            ('start', 'Start'),
            ('configure', 'Configure'),
            ('custom', 'Customize'),
            ('final', 'Final'),
        ]

    @api.model
    def _default_prescription_id(self):
        return self.env.context.get('active_id')

    def state_exit_start(self):
        self.state = 'configure'

    def state_exit_configure(self):
        self.state = 'custom'

    def state_exit_custom(self):
        self.state = 'final'

        # def state_exit_start(self):
    #     self.state = "final"

    # def state_previous_configure(self):
    #     self.state = 'start'

    def state_previous_custom(self):
        self.state = 'configure'

    def state_previous_final(self):
        self.state = 'custom'

    # right_photo = fields.Image("Right Photo")
    # left_photo = fields.Image("Left Photo")
    # left_obj_model = fields.Binary("Left Obj")
    # left_obj_file_name = fields.Char(string="Left Obj File Name")
    # right_obj_model = fields.Binary("Right Obj")
    # right_obj_file_name = fields.Char(string="Right Obj File Name")
    # right_photo = fields.Binary(related="patient_id.right_photo")
    # left_photo = fields.Binary(related="patient_id.left_photo")

    # foot_image1 = fields.Binary(related="patient_id.left_photo")
    # foot_image2 = fields.Binary(related="patient_id.right_photo")
    # foot_image1 = fields.Binary(related="prescription_id.foot_image1")
    # foot_image2 = fields.Binary(related="prescription_id.foot_image2")

    # l_foot_only = fields.Boolean('Left Only')
    # r_foot_only = fields.Boolean('Right Only')
    # b_l_pair = fields.Boolean('Bilateral')
    # l_r_mirror = fields.Boolean('Mirror Options', default=True)
    # left_only = fields.Boolean('Left Only')
    # right_only = fields.Boolean('Right Only')
    # field_name = fields.Boolean(string="check box", default=False)
    # bilateral = fields.Boolean('Bilateral', default=True)
    # mirror_options = fields.Boolean('Mirror Options', default=True)

    # price = fields.Float(compute=onchange_product, string='Price', store=True)
    # qty_available = fields.Integer(
    #     compute=onchange_product, string='Quantity Available', store=True)
    # pathologies = fields.Text('Pathologies')
    # pathology = fields.Char('Pathology')
    # laterality = fields.Selection(
    #     [('left', 'Left Only'), ('right', 'Right Only'), ('bilateral', 'Bilateral')], help="""" """)
    # notes = fields.Text('Extra Info')
    # allow_substitution = fields.Boolean('Allow Substitution')
    # form = fields.Char('Form')
    # prnt = fields.Boolean('Print')
    # quantity = fields.Float('Quantity')
    # quantity_unit_id = fields.Many2one(
    #     'podiatry.quantity.unit', 'Quantity Unit')
    # qty = fields.Integer('x')
    # device_quantity_id = fields.Many2one(
    #     'podiatry.device.quantity', 'Quantity')
    # quantity = fields.Integer('Quantity')
    # short_comment = fields.Char('Comment', size=128)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
