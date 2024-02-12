# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.tools.misc import get_lang


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    prescription_line_ids = fields.One2many('prescription.line', 'sale_line_id', string="Generated Prescription Lines", readonly=True, help="Prescription line generated by this Sales item on order confirmation, or when the quantity was increased.")
    prescription_line_count = fields.Integer("Number of generated prescription items", compute='_compute_prescription_count')

    @api.depends('prescription_line_ids')
    def _compute_prescription_count(self):
        database_data = self.env['prescription.line'].sudo()._read_group([('sale_line_id', 'in', self.ids)], ['sale_line_id'], ['__count'])
        mapped_data = {sale_line.id: count for sale_line, count in database_data}
        for line in self:
            line.prescription_line_count = mapped_data.get(line.id, 0)

    @api.onchange('product_uom_qty')
    def _onchange_service_product_uom_qty(self):
        if self.state == 'sale' and self.product_id.type == 'service' and self.product_id.service_to_prescription:
            if self.product_uom_qty < self._origin.product_uom_qty:
                if self.product_uom_qty < self.qty_delivered:
                    return {}
                warning_mess = {
                    'title': _('Ordered quantity decreased!'),
                    'message': _('You are decreasing the ordered quantity! Do not forget to manually update the prescription order if needed.'),
                }
                return {'warning': warning_mess}
        return {}

    # --------------------------
    # CRUD
    # --------------------------

    @api.model_create_multi
    def create(self, values):
        lines = super(SaleOrderLine, self).create(values)
        # Do not generate prescription when expense SO line since the product is already delivered
        lines.filtered(
            lambda line: line.state == 'sale' and not line.is_expense
        )._prescription_service_generation()
        return lines

    def write(self, values):
        increased_lines = None
        decreased_lines = None
        increased_values = {}
        decreased_values = {}
        if 'product_uom_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            increased_lines = self.sudo().filtered(lambda r: r.product_id.service_to_prescription and r.prescription_line_count and float_compare(r.product_uom_qty, values['product_uom_qty'], precision_digits=precision) == -1)
            decreased_lines = self.sudo().filtered(lambda r: r.product_id.service_to_prescription and r.prescription_line_count and float_compare(r.product_uom_qty, values['product_uom_qty'], precision_digits=precision) == 1)
            increased_values = {line.id: line.product_uom_qty for line in increased_lines}
            decreased_values = {line.id: line.product_uom_qty for line in decreased_lines}

        result = super(SaleOrderLine, self).write(values)

        if increased_lines:
            increased_lines._prescription_increase_ordered_qty(values['product_uom_qty'], increased_values)
        if decreased_lines:
            decreased_lines._prescription_decrease_ordered_qty(values['product_uom_qty'], decreased_values)
        return result

    # --------------------------
    # Business Methods
    # --------------------------

    def _prescription_decrease_ordered_qty(self, new_qty, origin_values):
        """ Decrease the quantity from SO line will add a next acitivities on the related prescription order
            :param new_qty: new quantity (lower than the current one on SO line), expressed
                in UoM of SO line.
            :param origin_values: map from sale line id to old value for the ordered quantity (dict)
        """
        prescription_to_notify_map = {}  # map PO -> set(SOL)
        last_prescription_lines = self.env['prescription.line'].search([('sale_line_id', 'in', self.ids)])
        for prescription_line in last_prescription_lines:
            prescription_to_notify_map.setdefault(prescription_line.order_id, self.env['sale.order.line'])
            prescription_to_notify_map[prescription_line.order_id] |= prescription_line.sale_line_id

        # create next activity
        for prescription, sale_lines in prescription_to_notify_map.items():
            render_context = {
                'sale_lines': sale_lines,
                'sale_orders': sale_lines.mapped('order_id'),
                'origin_values': origin_values,
            }
            prescription._activity_schedule_with_view('mail.mail_activity_data_warning',
                user_id=prescription.user_id.id or self.env.uid,
                views_or_xmlid='sale_prescription.exception_prescription_on_sale_quantity_decreased',
                render_context=render_context)

    def _prescription_increase_ordered_qty(self, new_qty, origin_values):
        """ Increase the quantity on the related prescription lines
            :param new_qty: new quantity (higher than the current one on SO line), expressed
                in UoM of SO line.
            :param origin_values: map from sale line id to old value for the ordered quantity (dict)
        """
        for line in self:
            last_prescription_line = self.env['prescription.line'].search([('sale_line_id', '=', line.id)], order='create_date DESC', limit=1)
            if last_prescription_line.state in ['draft', 'sent', 'to approve']:  # update qty for draft PO lines
                quantity = line.product_uom._compute_quantity(new_qty, last_prescription_line.product_uom)
                last_prescription_line.write({'product_qty': quantity})
            elif last_prescription_line.state in ['prescription', 'done', 'cancel']:  # create new PO, by forcing the quantity as the difference from SO line
                quantity = line.product_uom._compute_quantity(new_qty - origin_values.get(line.id, 0.0), last_prescription_line.product_uom)
                line._prescription_service_create(quantity=quantity)

    def _prescription_get_date_order(self, supplierinfo):
        """ return the ordered date for the prescription order, computed as : SO commitment date - supplier delay """
        commitment_date = fields.Datetime.from_string(self.order_id.commitment_date or fields.Datetime.now())
        return commitment_date - relativedelta(days=int(supplierinfo.delay))

    def _prescription_service_get_company(self):
        return self.company_id

    def _prescription_service_prepare_order_values(self, supplierinfo):
        """ Returns the values to create the prescription order from the current SO line.
            :param supplierinfo: record of product.supplierinfo
            :rtype: dict
        """
        self.ensure_one()
        partner_supplier = supplierinfo.partner_id
        fpos = self.env['account.fiscal.position'].sudo()._get_fiscal_position(partner_supplier)
        date_order = self._prescription_get_date_order(supplierinfo)
        return {
            'partner_id': partner_supplier.id,
            'partner_ref': partner_supplier.ref,
            'company_id': self._prescription_service_get_company().id,
            'currency_id': partner_supplier.property_prescription_currency_id.id or self.env.company.currency_id.id,
            'dest_address_id': False, # False since only supported in stock
            'origin': self.order_id.name,
            'payment_term_id': partner_supplier.property_supplier_payment_term_id.id,
            'date_order': date_order,
            'fiscal_position_id': fpos.id,
        }

    def _prescription_service_get_price_unit_and_taxes(self, supplierinfo, prescription):
        supplier_taxes = self.product_id.supplier_taxes_id.filtered(lambda t: t.company_id == prescription.company_id)
        taxes = prescription.fiscal_position_id.map_tax(supplier_taxes)
        if supplierinfo:
            price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price, supplier_taxes, taxes, prescription.company_id)
            if prescription.currency_id and supplierinfo.currency_id != prescription.currency_id:
                price_unit = supplierinfo.currency_id._convert(
                    price_unit,
                    prescription.currency_id,
                    prescription.company_id,
                    fields.Date.context_today(self)
                )
        else:
            price_unit = 0.0
        return price_unit, taxes

    def _prescription_service_get_product_name(self, supplierinfo, prescription, quantity):
        product_ctx = {
            'lang': get_lang(self.env, prescription.partner_id.lang).code,
            'company_id': prescription.company_id.id,
        }
        if supplierinfo:
            product_ctx.update({'seller_id': supplierinfo.id})
        else:
            product_ctx.update({'partner_id': prescription.partner_id.id})
        product = self.product_id.with_context(**product_ctx)
        name = product.display_name
        if product.description_prescription:
            name += '\n' + product.description_prescription
        return name

    def _prescription_service_prepare_line_values(self, prescription, quantity=False):
        """ Returns the values to create the prescription order line from the current SO line.
            :param prescription: record of prescription
            :rtype: dict
            :param quantity: the quantity to force on the PO line, expressed in SO line UoM
        """
        self.ensure_one()
        # compute quantity from SO line UoM
        product_quantity = self.product_uom_qty
        if quantity:
            product_quantity = quantity

        prescription_qty_uom = self.product_uom._compute_quantity(product_quantity, self.product_id.uom_po_id)

        # determine vendor (real supplier, sharing the same partner as the one from the PO, but with more accurate informations like validity, quantity, ...)
        # Note: one partner can have multiple supplier info for the same product
        supplierinfo = self.product_id._select_seller(
            partner_id=prescription.partner_id,
            quantity=prescription_qty_uom,
            date=prescription.date_order and prescription.date_order.date(), # and prescription.date_order[:10],
            uom_id=self.product_id.uom_po_id
        )

        price_unit, taxes = self._prescription_service_get_price_unit_and_taxes(supplierinfo, prescription)
        name = self._prescription_service_get_product_name(supplierinfo, prescription, quantity)

        line_description = self.with_context(lang=self.order_id.partner_id.lang)._get_sale_order_line_multiline_description_variants()
        if line_description:
            name += line_description

        return {
            'name': name,
            'product_qty': prescription_qty_uom,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'price_unit': price_unit,
            'date_planned': prescription.date_order + relativedelta(days=int(supplierinfo.delay)),
            'taxes_id': [(6, 0, taxes.ids)],
            'order_id': prescription.id,
            'sale_line_id': self.id,
        }

    def _prescription_service_match_supplier(self, warning=True):
        # determine vendor of the order (take the first matching company and product)
        suppliers = self.product_id._select_seller(partner_id=self._retrieve_prescription_partner(), quantity=self.product_uom_qty, uom_id=self.product_uom)
        if warning and not suppliers:
            raise UserError(_("There is no vendor associated to the product %s. Please define a vendor for this product.", self.product_id.display_name))
        return suppliers[0]

    def _prescription_service_match_prescription(self, partner, company=False):
        return self.env['prescription'].search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'draft'),
            ('company_id', '=', (company and company or self.env.company).id),
        ], order='id desc')

    def _create_prescription(self, supplierinfo):
        values = self._prescription_service_prepare_order_values(supplierinfo)
        return self.env['prescription'].with_context(mail_create_nosubscribe=True).create(values)

    def _match_or_create_prescription(self, supplierinfo):
        prescription = self._prescription_service_match_prescription(supplierinfo.partner_id)[:1]
        if not prescription:
            prescription = self._create_prescription(supplierinfo)
        return prescription

    def _retrieve_prescription_partner(self):
        """ In case we want to explicitely name a partner from whom we want to buy or receive products
        """
        self.ensure_one()
        return False

    def _prescription_service_create(self, quantity=False):
        """ On Sales Order confirmation, some lines (services ones) can create a prescription order line and maybe a prescription order.
            If a line should create a RFQ, it will check for existing PO. If no one is find, the SO line will create one, then adds
            a new PO line. The created prescription order line will be linked to the SO line.
            :param quantity: the quantity to force on the PO line, expressed in SO line UoM
        """
        supplier_po_map = {}
        sale_line_prescription_map = {}

        for line in self:
            line = line.with_company(line._prescription_service_get_company())
            supplierinfo = line._prescription_service_match_supplier()
            partner_supplier = supplierinfo.partner_id

            # determine (or create) PO
            prescription = supplier_po_map.get(partner_supplier.id)
            if not prescription:
                prescription = line._match_or_create_prescription(supplierinfo)
            else:  # if not already updated origin in this loop
                so_name = line.order_id.name
                origins = (prescription.origin or '').split(', ')
                if so_name not in origins:
                    prescription.write({'origin': ', '.join(origins + [so_name])})
            supplier_po_map[partner_supplier.id] = prescription

            # add a PO line to the PO
            values = line._prescription_service_prepare_line_values(prescription, quantity=quantity)
            prescription_line = line.env['prescription.line'].create(values)

            # link the generated prescription to the SO line
            sale_line_prescription_map.setdefault(line, line.env['prescription.line'])
            sale_line_prescription_map[line] |= prescription_line
        return sale_line_prescription_map

    def _prescription_service_generation(self):
        """ Create a Prescription for the first time from the sale line. If the SO line already created a PO, it
            will not create a second one.
        """
        sale_line_prescription_map = {}
        for line in self:
            # Do not regenerate PO line if the SO line has already created one in the past (SO cancel/reconfirmation case)
            if line.product_id.service_to_prescription and not line.prescription_line_count:
                result = line._prescription_service_create()
                sale_line_prescription_map.update(result)
        return sale_line_prescription_map
