# -*- coding: utf-8 -*-


from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_downpayment = fields.Boolean()
    prescription_line_ids = fields.Many2many(
        'prescription.order.line',
        'prescription_order_line_invoice_rel',
        'invoice_line_id', 'order_line_id',
        string='Prescription Order Lines', readonly=True, copy=False)

    def _copy_data_extend_business_fields(self, values):
        # OVERRIDE to copy the 'prescription_line_ids' field as well.
        super(AccountMoveLine, self)._copy_data_extend_business_fields(values)
        values['prescription_line_ids'] = [(6, None, self.prescription_line_ids.ids)]

    def _prepare_analytic_lines(self):
        """ Note: This method is called only on the move.line that having an analytic distribution, and
            so that should create analytic entries.
        """
        values_list = super(AccountMoveLine, self)._prepare_analytic_lines()

        # filter the move lines that can be reinvoiced: a cost (negative amount) analytic line without SO line but with a product can be reinvoiced
        move_to_reinvoice = self.env['account.move.line']
        if len(values_list) > 0:
            for index, move_line in enumerate(self):
                values = values_list[index]
                if 'so_line' not in values:
                    if move_line._prescription_can_be_reinvoice():
                        move_to_reinvoice |= move_line

        # insert the prescription line in the create values of the analytic entries
        if move_to_reinvoice:
            map_prescription_line_per_move = move_to_reinvoice._prescription_create_reinvoice_prescription_line()
            for values in values_list:
                prescription_line = map_prescription_line_per_move.get(values.get('move_line_id'))
                if prescription_line:
                    values['so_line'] = prescription_line.id

        return values_list

    def _prescription_can_be_reinvoice(self):
        """ determine if the generated analytic line should be reinvoiced or not.
            For Vendor Bill flow, if the product has a 'erinvoice policy' and is a cost, then we will find the SO on which reinvoice the AAL
        """
        self.ensure_one()
        if self.prescription_line_ids:
            return False
        uom_precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        return float_compare(self.credit or 0.0, self.debit or 0.0, precision_digits=uom_precision_digits) != 1 and self.product_id.expense_policy not in [False, 'no']

    def _prescription_create_reinvoice_prescription_line(self):

        prescription_order_map = self._prescription_determine_order()

        prescription_line_values_to_create = []  # the list of creation values of prescription line to create.
        existing_prescription_line_cache = {}  # in the prescription_price-delivery case, we can reuse the same prescription line. This cache will avoid doing a search each time the case happen
        # `map_move_prescription_line` is map where
        #   - key is the move line identifier
        #   - value is either a prescription.order.line record (existing case), or an integer representing the index of the prescription line to create in
        #     the `prescription_line_values_to_create` (not existing case, which will happen more often than the first one).
        map_move_prescription_line = {}

        for move_line in self:
            prescription_order = prescription_order_map.get(move_line.id)

            # no reinvoice as no prescription order was found
            if not prescription_order:
                continue

            # raise if the prescription order is not currently open
            if prescription_order.state in ('draft', 'sent'):
                raise UserError(_(
                    "The Prescription Order %(order)s linked to the Analytic Account %(account)s must be"
                    " validated before registering expenses.",
                    order=prescription_order.name,
                    account=prescription_order.analytic_account_id.name,
                ))
            elif prescription_order.state == 'cancel':
                raise UserError(_(
                    "The Prescription Order %(order)s linked to the Analytic Account %(account)s is cancelled."
                    " You cannot register an expense on a cancelled Prescription Order.",
                    order=prescription_order.name,
                    account=prescription_order.analytic_account_id.name,
                ))
            elif prescription_order.locked:
                raise UserError(_(
                    "The Prescription Order %(order)s linked to the Analytic Account %(account)s is currently locked."
                    " You cannot register an expense on a locked Prescription Order."
                    " Please create a new SO linked to this Analytic Account.",
                    order=prescription_order.name,
                    account=prescription_order.analytic_account_id.name,
                ))

            price = move_line._prescription_get_invoice_price(prescription_order)

            # find the existing prescription.line or keep its creation values to process this in batch
            prescription_line = None
            if move_line.product_id.expense_policy == 'prescription_price' and move_line.product_id.invoice_policy == 'delivery':  # for those case only, we can try to reuse one
                map_entry_key = (prescription_order.id, move_line.product_id.id, price)  # cache entry to limit the call to search
                prescription_line = existing_prescription_line_cache.get(map_entry_key)
                if prescription_line:  # already search, so reuse it. prescription_line can be prescription.order.line record or index of a "to create values" in `prescription_line_values_to_create`
                    map_move_prescription_line[move_line.id] = prescription_line
                    existing_prescription_line_cache[map_entry_key] = prescription_line
                else:  # search for existing prescription line
                    prescription_line = self.env['prescription.order.line'].search([
                        ('order_id', '=', prescription_order.id),
                        ('price_unit', '=', price),
                        ('product_id', '=', move_line.product_id.id),
                        ('is_expense', '=', True),
                    ], limit=1)
                    if prescription_line:  # found existing one, so keep the browse record
                        map_move_prescription_line[move_line.id] = existing_prescription_line_cache[map_entry_key] = prescription_line
                    else:  # should be create, so use the index of creation values instead of browse record
                        # save value to create it
                        prescription_line_values_to_create.append(move_line._prescription_prepare_prescription_line_values(prescription_order, price))
                        # store it in the cache of existing ones
                        existing_prescription_line_cache[map_entry_key] = len(prescription_line_values_to_create) - 1  # save the index of the value to create prescription line
                        # store it in the map_move_prescription_line map
                        map_move_prescription_line[move_line.id] = len(prescription_line_values_to_create) - 1  # save the index of the value to create prescription line

            else:  # save its value to create it anyway
                prescription_line_values_to_create.append(move_line._prescription_prepare_prescription_line_values(prescription_order, price))
                map_move_prescription_line[move_line.id] = len(prescription_line_values_to_create) - 1  # save the index of the value to create prescription line

        # create the prescription lines in batch
        new_prescription_lines = self.env['prescription.order.line'].create(prescription_line_values_to_create)

        # build result map by replacing index with newly created record of prescription.order.line
        result = {}
        for move_line_id, unknown_prescription_line in map_move_prescription_line.items():
            if isinstance(unknown_prescription_line, int):  # index of newly created prescription line
                result[move_line_id] = new_prescription_lines[unknown_prescription_line]
            elif isinstance(unknown_prescription_line, models.BaseModel):  # already record of prescription.order.line
                result[move_line_id] = unknown_prescription_line
        return result

    def _prescription_determine_order(self):
        """ Get the mapping of move.line with the prescription.order record on which its analytic entries should be reinvoiced
            :return a dict where key is the move line id, and value is prescription.order record (or None).
        """
        mapping = {}
        for move_line in self:
            if move_line.analytic_distribution:
                distribution_json = move_line.analytic_distribution
                prescription_order = self.env['prescription.order'].search([('analytic_account_id', 'in', list(int(account_id) for account_id in distribution_json.keys())),
                                                            ('state', '=', 'prescription')], order='create_date ASC', limit=1)
                if prescription_order:
                    mapping[move_line.id] = prescription_order
                else:
                    prescription_order = self.env['prescription.order'].search([('analytic_account_id', 'in', list(int(account_id) for account_id in distribution_json.keys()))], order='create_date ASC', limit=1)
                    mapping[move_line.id] = prescription_order

        # map of AAL index with the SO on which it needs to be reinvoiced. Maybe be None if no SO found
        return mapping

    def _prescription_prepare_prescription_line_values(self, order, price):
        """ Generate the prescription.line creation value from the current move line """
        self.ensure_one()
        last_so_line = self.env['prescription.order.line'].search([('order_id', '=', order.id)], order='sequence desc', limit=1)
        last_sequence = last_so_line.sequence + 1 if last_so_line else 100

        fpos = order.fiscal_position_id or order.fiscal_position_id._get_fiscal_position(order.partner_id)
        product_taxes = self.product_id.taxes_id.filtered(lambda tax: tax.company_id == order.company_id)
        taxes = fpos.map_tax(product_taxes)

        return {
            'order_id': order.id,
            'name': self.name,
            'sequence': last_sequence,
            'price_unit': price,
            'tax_id': [x.id for x in taxes],
            'discount': 0.0,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': 0.0,
            'is_expense': True,
        }

    def _prescription_get_invoice_price(self, order):
        """ Based on the current move line, compute the price to reinvoice the analytic line that is going to be created (so the
            price of the prescription line).
        """
        self.ensure_one()

        unit_amount = self.quantity
        amount = (self.credit or 0.0) - (self.debit or 0.0)

        if self.product_id.expense_policy == 'prescription_price':
            return order.pricelist_id._get_product_price(
                self.product_id,
                1.0,
                uom=self.product_uom_id,
                date=order.date_order,
            )

        uom_precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        if float_is_zero(unit_amount, precision_digits=uom_precision_digits):
            return 0.0

        # Prevent unnecessary currency conversion that could be impacted by exchange rate
        # fluctuations
        if self.company_id.currency_id and amount and self.company_id.currency_id == order.currency_id:
            return self.company_id.currency_id.round(abs(amount / unit_amount))

        price_unit = abs(amount / unit_amount)
        currency_id = self.company_id.currency_id
        if currency_id and currency_id != order.currency_id:
            price_unit = currency_id._convert(price_unit, order.currency_id, order.company_id, order.date_order or fields.Date.today())
        return price_unit

    def _get_downpayment_lines(self):
        # OVERRIDE
        return self.prescription_line_ids.filtered('is_downpayment').invoice_lines.filtered(lambda line: line.move_id._is_downpayment())
