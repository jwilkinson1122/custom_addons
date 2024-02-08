# -*- coding: utf-8 -*-


from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_downpayment = fields.Boolean()
    prescriptions_line_ids = fields.Many2many(
        'prescriptions.order.line',
        'prescriptions_order_line_invoice_rel',
        'invoice_line_id', 'order_line_id',
        string='Prescriptions Order Lines', readonly=True, copy=False)

    def _copy_data_extend_business_fields(self, values):
        # OVERRIDE to copy the 'prescriptions_line_ids' field as well.
        super(AccountMoveLine, self)._copy_data_extend_business_fields(values)
        values['prescriptions_line_ids'] = [(6, None, self.prescriptions_line_ids.ids)]

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
                    if move_line._prescriptions_can_be_reinvoice():
                        move_to_reinvoice |= move_line

        # insert the prescriptions line in the create values of the analytic entries
        if move_to_reinvoice:
            map_prescriptions_line_per_move = move_to_reinvoice._prescriptions_create_reinvoice_prescriptions_line()
            for values in values_list:
                prescriptions_line = map_prescriptions_line_per_move.get(values.get('move_line_id'))
                if prescriptions_line:
                    values['so_line'] = prescriptions_line.id

        return values_list

    def _prescriptions_can_be_reinvoice(self):
        """ determine if the generated analytic line should be reinvoiced or not.
            For Vendor Bill flow, if the product has a 'erinvoice policy' and is a cost, then we will find the SO on which reinvoice the AAL
        """
        self.ensure_one()
        if self.prescriptions_line_ids:
            return False
        uom_precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        return float_compare(self.credit or 0.0, self.debit or 0.0, precision_digits=uom_precision_digits) != 1 and self.product_id.expense_policy not in [False, 'no']

    def _prescriptions_create_reinvoice_prescriptions_line(self):

        prescriptions_order_map = self._prescriptions_determine_order()

        prescriptions_line_values_to_create = []  # the list of creation values of prescriptions line to create.
        existing_prescriptions_line_cache = {}  # in the prescriptions_price-delivery case, we can reuse the same prescriptions line. This cache will avoid doing a search each time the case happen
        # `map_move_prescriptions_line` is map where
        #   - key is the move line identifier
        #   - value is either a prescriptions.order.line record (existing case), or an integer representing the index of the prescriptions line to create in
        #     the `prescriptions_line_values_to_create` (not existing case, which will happen more often than the first one).
        map_move_prescriptions_line = {}

        for move_line in self:
            prescriptions_order = prescriptions_order_map.get(move_line.id)

            # no reinvoice as no prescriptions order was found
            if not prescriptions_order:
                continue

            # raise if the prescriptions order is not currently open
            if prescriptions_order.state in ('draft', 'sent'):
                raise UserError(_(
                    "The Prescriptions Order %(order)s linked to the Analytic Account %(account)s must be"
                    " validated before registering expenses.",
                    order=prescriptions_order.name,
                    account=prescriptions_order.analytic_account_id.name,
                ))
            elif prescriptions_order.state == 'cancel':
                raise UserError(_(
                    "The Prescriptions Order %(order)s linked to the Analytic Account %(account)s is cancelled."
                    " You cannot register an expense on a cancelled Prescriptions Order.",
                    order=prescriptions_order.name,
                    account=prescriptions_order.analytic_account_id.name,
                ))
            elif prescriptions_order.locked:
                raise UserError(_(
                    "The Prescriptions Order %(order)s linked to the Analytic Account %(account)s is currently locked."
                    " You cannot register an expense on a locked Prescriptions Order."
                    " Please create a new SO linked to this Analytic Account.",
                    order=prescriptions_order.name,
                    account=prescriptions_order.analytic_account_id.name,
                ))

            price = move_line._prescriptions_get_invoice_price(prescriptions_order)

            # find the existing prescriptions.line or keep its creation values to process this in batch
            prescriptions_line = None
            if move_line.product_id.expense_policy == 'prescriptions_price' and move_line.product_id.invoice_policy == 'delivery':  # for those case only, we can try to reuse one
                map_entry_key = (prescriptions_order.id, move_line.product_id.id, price)  # cache entry to limit the call to search
                prescriptions_line = existing_prescriptions_line_cache.get(map_entry_key)
                if prescriptions_line:  # already search, so reuse it. prescriptions_line can be prescriptions.order.line record or index of a "to create values" in `prescriptions_line_values_to_create`
                    map_move_prescriptions_line[move_line.id] = prescriptions_line
                    existing_prescriptions_line_cache[map_entry_key] = prescriptions_line
                else:  # search for existing prescriptions line
                    prescriptions_line = self.env['prescriptions.order.line'].search([
                        ('order_id', '=', prescriptions_order.id),
                        ('price_unit', '=', price),
                        ('product_id', '=', move_line.product_id.id),
                        ('is_expense', '=', True),
                    ], limit=1)
                    if prescriptions_line:  # found existing one, so keep the browse record
                        map_move_prescriptions_line[move_line.id] = existing_prescriptions_line_cache[map_entry_key] = prescriptions_line
                    else:  # should be create, so use the index of creation values instead of browse record
                        # save value to create it
                        prescriptions_line_values_to_create.append(move_line._prescriptions_prepare_prescriptions_line_values(prescriptions_order, price))
                        # store it in the cache of existing ones
                        existing_prescriptions_line_cache[map_entry_key] = len(prescriptions_line_values_to_create) - 1  # save the index of the value to create prescriptions line
                        # store it in the map_move_prescriptions_line map
                        map_move_prescriptions_line[move_line.id] = len(prescriptions_line_values_to_create) - 1  # save the index of the value to create prescriptions line

            else:  # save its value to create it anyway
                prescriptions_line_values_to_create.append(move_line._prescriptions_prepare_prescriptions_line_values(prescriptions_order, price))
                map_move_prescriptions_line[move_line.id] = len(prescriptions_line_values_to_create) - 1  # save the index of the value to create prescriptions line

        # create the prescriptions lines in batch
        new_prescriptions_lines = self.env['prescriptions.order.line'].create(prescriptions_line_values_to_create)

        # build result map by replacing index with newly created record of prescriptions.order.line
        result = {}
        for move_line_id, unknown_prescriptions_line in map_move_prescriptions_line.items():
            if isinstance(unknown_prescriptions_line, int):  # index of newly created prescriptions line
                result[move_line_id] = new_prescriptions_lines[unknown_prescriptions_line]
            elif isinstance(unknown_prescriptions_line, models.BaseModel):  # already record of prescriptions.order.line
                result[move_line_id] = unknown_prescriptions_line
        return result

    def _prescriptions_determine_order(self):
        """ Get the mapping of move.line with the prescriptions.order record on which its analytic entries should be reinvoiced
            :return a dict where key is the move line id, and value is prescriptions.order record (or None).
        """
        mapping = {}
        for move_line in self:
            if move_line.analytic_distribution:
                distribution_json = move_line.analytic_distribution
                prescriptions_order = self.env['prescriptions.order'].search([('analytic_account_id', 'in', list(int(account_id) for account_id in distribution_json.keys())),
                                                            ('state', '=', 'prescriptions')], order='create_date ASC', limit=1)
                if prescriptions_order:
                    mapping[move_line.id] = prescriptions_order
                else:
                    prescriptions_order = self.env['prescriptions.order'].search([('analytic_account_id', 'in', list(int(account_id) for account_id in distribution_json.keys()))], order='create_date ASC', limit=1)
                    mapping[move_line.id] = prescriptions_order

        # map of AAL index with the SO on which it needs to be reinvoiced. Maybe be None if no SO found
        return mapping

    def _prescriptions_prepare_prescriptions_line_values(self, order, price):
        """ Generate the prescriptions.line creation value from the current move line """
        self.ensure_one()
        last_so_line = self.env['prescriptions.order.line'].search([('order_id', '=', order.id)], order='sequence desc', limit=1)
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

    def _prescriptions_get_invoice_price(self, order):
        """ Based on the current move line, compute the price to reinvoice the analytic line that is going to be created (so the
            price of the prescriptions line).
        """
        self.ensure_one()

        unit_amount = self.quantity
        amount = (self.credit or 0.0) - (self.debit or 0.0)

        if self.product_id.expense_policy == 'prescriptions_price':
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
        return self.prescriptions_line_ids.filtered('is_downpayment').invoice_lines.filtered(lambda line: line.move_id._is_downpayment())
