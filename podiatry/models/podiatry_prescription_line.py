# -*- coding: utf-8 -*-
import logging
from datetime import date, datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import get_lang


_logger = logging.getLogger(__name__)


class PrescriptionLine(models.Model):
    _name = "podiatry.prescription.line"
    _description = 'podiatry prescription line'
    _rec_name = 'product_id'

    # @api.depends('product_id')
    # def _onchange_product_id(self):
    #     for each in self:
    #         if each:
    #             self.qty_available = self.product_id.qty_available
    #             self.price = self.product_id.lst_price
    #         else:
    #             self.qty_available = 0
    #             self.price = 0.0
    @api.depends('product_id')
    def _onchange_product_id(self):
        for each in self:
            if each:
                self.qty_available = self.product_id.qty_available
                self.price = self.product_id.lst_price
            else:
                self.qty_available = 0
                self.price = 0.0
    
    # name = fields.Many2one('podiatry.prescription', 'Rx ID')
    name = fields.Text(string='Description')
    prescription_id = fields.Many2one("podiatry.prescription", "Prescription Number", ondelete="cascade")
    # prescription_line_id = fields.Many2one("podiatry.prescription.line","Prescription Line", required=True, delegate=True, ondelete="cascade")
    practitioner_id = fields.Many2one("podiatry.practitioner")
    practitioner = fields.Char(
        related='prescription_id.practitioner_id.name')
    patient_id = fields.Many2one("podiatry.patient")
    patient = fields.Char(
        related='prescription_id.patient_id.name')
    product_id = fields.Many2one('product.product', 'Name')
    product_updatable = fields.Boolean(compute='_compute_product_updatable', string='Can Edit Product', default=True)
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0) 
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]", ondelete="restrict")
    product_template_id = fields.Many2one(
        'product.template', string='Product Template',
        related="product_id.product_tmpl_id")
    qty_available = fields.Integer(compute=_onchange_product_id,string='Quantity Available',store=True)
    # qty_delivered = fields.Float('Delivered Quantity', copy=False, compute='_compute_qty_delivered', inverse='_inverse_qty_delivered', store=True, digits='Product Unit of Measure', default=0.0)
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'prescription_line_id', string="Custom Values", copy=True)
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string="Extra Values", ondelete='restrict')
    
    state = fields.Selection(
        related='prescription_id.state', string='Prescription Status', copy=False, store=True)

    
    price = fields.Float(
        string='Price', compute='_compute_price',
        digits='Product Price', readonly=False, store=True)
    
    @api.depends('product_id')
    def _compute_price(self):
        for line in self:
            if line.product_id and line.product_id.lst_price:
                line.price = line.product_id.lst_price or 0
            elif not line.price:
                line.price = 0

    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    name_short = fields.Char(compute="_compute_name_short")
    linked_line_id = fields.Many2one('podiatry.prescription.line', string='Linked Prescription Line', domain="[('prescription_id', '=', prescription_id)]", ondelete='cascade', copy=False, index=True)
    option_line_ids = fields.One2many('podiatry.prescription.line', 'linked_line_id', string='Options Linked')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    
    @api.depends('product_id', 'prescription_id.state')
    def _compute_product_updatable(self):
        for line in self:
            if line.state in ['done', 'cancel']:
                line.product_updatable = False
            else:
                line.product_updatable = True

    
    def get_prescription_line_multiline_description(self, product):
        description = super(PrescriptionLine, self).get_prescription_line_multiline_description(product)
        if self.linked_line_id:
            description += "\n" + _("Option for: %s", self.linked_line_id.product_id.display_name)
        if self.option_line_ids:
            description += "\n" + '\n'.join([_("Option: %s", option_line.product_id.display_name) for option_line in self.option_line_ids])
        return description

    @api.depends('product_id.display_name')
    def _compute_name_short(self):
        """ Compute a short name for this prescription order line, to be used on the website where we don't have much space.
            To keep it short, instead of using the first line of the description, we take the product name without the internal reference.
        """
        for record in self:
            record.name_short = record.product_id.with_context(display_default_code=False).display_name

    def get_description_following_lines(self):
        return self.name.splitlines()[1:]



    # @api.model
    # def _selection_state(self):
    #     return [
    #         ('start', 'Start'),
    #         ('configure', 'Configure'),
    #         ('custom', 'Customize'),
    #         ('final', 'Final'),
    #     ]

    # @api.model
    # def _default_prescription_id(self):
    #     return self.env.context.get('active_id')

    # def state_exit_start(self):
    #     self.state = 'configure'

    # def state_exit_configure(self):
    #     self.state = 'custom'

    # def state_exit_custom(self):
    #     self.state = 'final'

    # def state_previous_custom(self):
    #     self.state = 'configure'

    # def state_previous_final(self):
    #     self.state = 'custom'


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
