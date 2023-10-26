# -*- coding: utf-8 -*-


import base64

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression


class PrescriptionProduct(models.Model):
    """ Products available to order. A product is linked to a specific partner. """
    _name = 'prescription.product'
    _description = 'Prescription Product'
    _inherit = 'image.mixin'
    _order = 'name'
    _check_company_auto = True

    name = fields.Char('Product Name', required=True, translate=True)
    category_id = fields.Many2one('prescription.product.category', 'Product Category', check_company=True, required=True)
    description = fields.Html('Description', translate=True)
    price = fields.Float('Price', digits='Account', required=True)
    partner_id = fields.Many2one('prescription.partner', 'Partner', check_company=True, required=True)
    active = fields.Boolean(default=True)

    company_id = fields.Many2one('res.company', related='partner_id.company_id', readonly=False, store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    new_until = fields.Date('New Until')
    is_new = fields.Boolean(compute='_compute_is_new')

    favorite_user_ids = fields.Many2many('res.users', 'prescription_product_favorite_user_rel', 'product_id', 'user_id', check_company=True)
    # favorite_partner_ids = fields.Many2many('res.partner', 'prescription_product_favorite_partner_rel', 'product_id', 'partner_id')

    is_favorite = fields.Boolean(compute='_compute_is_favorite', inverse='_inverse_is_favorite')

    last_order_date = fields.Date(compute='_compute_last_order_date')

    product_image = fields.Image(compute='_compute_product_image')
    # This field is used only for searching
    is_available_at = fields.Many2one('prescription.location', 'Product Availability', compute='_compute_is_available_at', search='_search_is_available_at')

    @api.depends('image_128', 'category_id.image_128')
    def _compute_product_image(self):
        for product in self:
            product.product_image = product.image_128 or product.category_id.image_128

    @api.depends('new_until')
    def _compute_is_new(self):
        today = fields.Date.context_today(self)
        for product in self:
            if product.new_until:
                product.is_new = today <= product.new_until
            else:
                product.is_new = False

    # @api.depends_context('uid', 'partner_id')
    # @api.depends('favorite_user_ids', 'favorite_partner_ids')
    # def _compute_is_favorite(self):
    #     for product in self: 
    #         if product.is_favorite:
    #             product = self.env.user in product.favorite_user_ids
    #         else:
    #             product = self.partner_id in product.favorite_partner_ids
 
    @api.depends_context('uid')
    @api.depends('favorite_user_ids')
    def _compute_is_favorite(self):
        for product in self:
             product.is_favorite = self.env.user in product.favorite_user_ids
             
    @api.depends_context('uid')
    def _compute_last_order_date(self):
        all_orders = self.env['prescription.order'].search([
            ('user_id', '=', self.env.user.id),
            ('product_id', 'in', self.ids),
        ])
        mapped_orders = defaultdict(lambda: self.env['prescription.order'])
        for order in all_orders:
            mapped_orders[order.product_id] |= order
        for product in self:
            if not mapped_orders[product]:
                product.last_order_date = False
            else:
                product.last_order_date = max(mapped_orders[product].mapped('date'))

    def _compute_is_available_at(self):
        """
            Is available_at is always false when browsing it
            this field is there only to search (see _search_is_available_at)
        """
        for product in self:
            product.is_available_at = False

    def _search_is_available_at(self, operator, value):
        supported_operators = ['in', 'not in', '=', '!=']

        if not operator in supported_operators:
            return expression.TRUE_DOMAIN

        if isinstance(value, int):
            value = [value]

        if operator in expression.NEGATIVE_TERM_OPERATORS:
            return expression.AND([[('partner_id.available_location_ids', 'not in', value)], [('partner_id.available_location_ids', '!=', False)]])

        return expression.OR([[('partner_id.available_location_ids', 'in', value)], [('partner_id.available_location_ids', '=', False)]])

    def _sync_active_from_related(self):
        """ Archive/unarchive product after related field is archived/unarchived """
        return self.filtered(lambda p: (p.category_id.active and p.partner_id.active) != p.active).toggle_active()

    def toggle_active(self):
        invalid_products = self.filtered(lambda product: not product.active and not product.category_id.active)
        if invalid_products:
            raise UserError(_("The following product categories are archived. You should either unarchive the categories or change the category of the product.\n%s", '\n'.join(invalid_products.category_id.mapped('name'))))
        invalid_products = self.filtered(lambda product: not product.active and not product.partner_id.active)
        if invalid_products:
            raise UserError(_("The following partners are archived. You should either unarchive the partners or change the partner of the product.\n%s", '\n'.join(invalid_products.partner_id.mapped('name'))))
        return super().toggle_active()

    def _inverse_is_favorite(self):
        """ Handled in the write() """
        pass

    def write(self, vals):
        if 'is_favorite' in vals:
            if vals.pop('is_favorite'):
                commands = [(4, product.id) for product in self]
            else:
                commands = [(3, product.id) for product in self]
            self.env.user.write({
                'favorite_prescription_product_ids': commands,
            })

        if not vals:
            return True
        return super().write(vals)
