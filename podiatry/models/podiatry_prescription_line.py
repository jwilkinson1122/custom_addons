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
  
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        self._update_description()
        product = self.product_id
        if product and product.sale_line_warn != 'no-message':
            if product.sale_line_warn == 'block':
                self.product_id = False
            return {
                'warning': {
                    'title': _("Warning for %s", product.name),
                    'message': product.sale_line_warn_msg,
                }
            }

    def _update_description(self):
        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        lang = get_lang(self.env, self.prescription_id.partner_id.lang).code
        product = self.product_id.with_context(
            lang=lang,
        )

        self.update({'name': self.with_context(lang=lang).get_prescription_line_multiline_description(product)})

    
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
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0) 
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]", ondelete="restrict")
    product_template_id = fields.Many2one(
        'product.template', string='Product Template',
        related="product_id.product_tmpl_id")
    qty_available = fields.Integer(compute=_onchange_product_id,string='Quantity Available',store=True)
    # qty_delivered = fields.Float('Delivered Quantity', copy=False, compute='_compute_qty_delivered', inverse='_inverse_qty_delivered', store=True, digits='Product Unit of Measure', default=0.0)
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'prescription_line_id', string="Custom Values", copy=True)
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string="Extra Values", ondelete='restrict')
    sequence = fields.Integer(string='Sequence', default=10)
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
        return product.get_product_multiline_description_prescription() + self._get_prescription_line_multiline_description_variants()

    def _get_prescription_line_multiline_description_variants(self):
        if not self.product_custom_attribute_value_ids and not self.product_no_variant_attribute_value_ids:
            return ""

        name = "\n"

        custom_ptavs = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id
        no_variant_ptavs = self.product_no_variant_attribute_value_ids._origin

        # display the no_variant attributes, except those that are also
        # displayed by a custom (avoid duplicate description)
        for ptav in (no_variant_ptavs - custom_ptavs):
            name += "\n" + ptav.display_name

        # Sort the values according to _order settings, because it doesn't work for virtual records in onchange
        custom_values = sorted(self.product_custom_attribute_value_ids, key=lambda r: (r.custom_product_template_attribute_value_id.id, r.id))
        # display the is_custom values
        for pacv in custom_values:
            name += "\n" + pacv.display_name

        return name

    def _is_not_sellable_line(self):
        # True if the line is a computed line (reward, delivery, ...) that user cannot add manually
        return False

    
    # def get_prescription_line_multiline_description(self, product):
    #     description = super(PrescriptionLine, self).get_prescription_line_multiline_description(product)
    #     if self.linked_line_id:
    #         description += "\n" + _("Option for: %s", self.linked_line_id.product_id.display_name)
    #     if self.option_line_ids:
    #         description += "\n" + '\n'.join([_("Option: %s", option_line.product_id.display_name) for option_line in self.option_line_ids])
    #     return description

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
