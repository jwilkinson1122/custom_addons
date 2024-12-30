from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from itertools import groupby
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_booking = fields.Boolean(string='Is Booking', default=False)
    date_created = fields.Datetime(string='Creation Date', default=fields.Datetime.now)
    rfq_created = fields.Boolean(string="RFQ Created", default=False)
    expired_three_days = fields.Boolean(string='Expire in 3 Day',
                                        compute="_compute_expire_in_three_days", store=True)

    @api.model
    def create(self, vals):
        if vals.get('is_booking'):
            sequence_code = 'booking.order'
        else:
            sequence_code = 'sale.order'
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code) or _('New')
        res = super(SaleOrder, self).create(vals)
        return res

    # ir.cron
    # cancel after 3 day if not process
    @api.model
    def _cancel_unprocessed_orders(self):
        record_three_days = fields.Datetime.to_string(datetime.now() + timedelta(days=3))
        unprocessed_orders = self.env['sale.order'].search([
            ('create_date', '<', record_three_days),
            ('state', '=', 'draft'),
            ('is_booking', '=', True)
        ])
        for order in unprocessed_orders:
            order.action_cancel()

        return True

    # masih perlu diuji coba
    @api.depends('create_date', 'state', 'is_booking')
    def _compute_expire_in_three_days(self):
        today = datetime.now()
        start_date = today + timedelta(days=3)
        for order in self:
            if order.state == 'draft' and order.is_booking and order.create_date:
                create_date = fields.Datetime.from_string(order.create_date)
                order.expired_three_days = start_date <= create_date
            else:
                order.expired_three_days = False

    @api.onchange('date_order')
    def _onchange_date_order(self):
        if self.date_order:
            self.validity_date = self.date_order + timedelta(days=3)

    def action_create_rfq(self):
        for record in self:
            if record.rfq_created:
                raise ValidationError(f'Product {record.name} already been added to RFQ.')
            sequence_name = self.env['ir.sequence'].next_by_code('request.quotation') or _('New')
            rfq = self.env['purchase.order'].create({
                'partner_id': record.partner_id.id,
                'date_order': fields.Datetime.now(),
                'name': sequence_name,
                'is_booking': True,
                'order_line': [(0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'product_qty': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'date_planned': fields.Datetime.now(),
                }) for line in record.order_line]
            })
            record.rfq_created = True
            return {
                'name': 'RFQ Created',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'res_id': rfq.id,
                'view_mode': 'form',
            }

    # maximum limit per order
    @api.constrains('order_line')
    def _check_order_line_limit(self):
        config = self.env['booking.order.config'].search([], limit=1)
        if config:
            for order in self:
                total_qty = sum(
                    line.product_id.qty_available + (
                            line.product_id.qty_available * config.qty_limit_percentage / 100)
                    for line in order.order_line
                )
                if total_qty > config.max_booking_order:
                    raise ValidationError('Total booking quantity exceeds the maximum limit per order.')

    # refresh price
    def action_refresh_price(self):
        self.ensure_one()
        for line in self.order_line:
            line.price_unit = line.product_id.list_price

    # fitur optional (send whatsapp message)
    def action_send_whatsapp(self):
        """ Action for sending whatsapp message."""
        compose_form_id = self.env.ref(
            'final_exam_hashmicro.whatsapp_send_message_view_form').id
        ctx = dict(self.env.context)
        message = ("Hi" + " " + self.partner_id.name + ',' + '\n' +
                   "Your quotation" + ' ' + self.name + ' ' + "amounting" + ' '
                   + str(self.amount_total) + self.currency_id.symbol + ' ' +
                   "is ready for review.Do not hesitate to contact us if you "
                   "have any questions.")
        ctx.update({
            'default_message': message,
            'default_partner_id': self.partner_id.id,
            'default_mobile': self.partner_id.mobile,
            'default_image_1920': self.partner_id.image_1920,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'whatsapp.send.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def check_customers(self, partner_ids):
        """ Check if the selected sale orders belong to the same customer."""
        partners = groupby(partner_ids)
        return next(partners, True) and not next(partners, False)

    def action_whatsapp_multi(self):
        """
        Initiate WhatsApp messaging for multiple sale orders and open a message
        composition wizard.
        """
        sale_order_ids = self.env['sale.order'].browse(
            self.env.context.get('active_ids'))
        partner_ids = []
        for sale in sale_order_ids:
            partner_ids.append(sale.partner_id.id)
        partner_check = self.check_customers(partner_ids)
        if partner_check:
            sale_numbers = sale_order_ids.mapped('name')
            sale_numbers = "\n".join(sale_numbers)
            compose_form_id = self.env.ref(
                'final_exam_hashmicro.whatsapp_send_message_view_form').id
            ctx = dict(self.env.context)
            message = ("Hi" + " " + self.partner_id.name + ',' + '\n' +
                       "Your Orders are" + '\n' + sale_numbers + ' ' + '\n' +
                       "is ready for review.Do not hesitate to contact us if "
                       "you have any questions.")
            ctx.update({
                'default_message': message,
                'default_partner_id': sale_order_ids[0].partner_id.id,
                'default_mobile': sale_order_ids[0].partner_id.mobile,
                'default_image_1920': sale_order_ids[0].partner_id.image_1920,
            })
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'whatsapp.send.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }
        else:
            raise UserError(_(
                'It appears that you have selected orders from multiple'
                ' customers. Please select orders from a single customer.'))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_booking = fields.Float(string='Quantity Booking', default=1.0, store=True)
    product_template_id = fields.Many2one('product.template', string='Product Template',
                                          compute='_compute_product_template_id')

    @api.onchange('product_uom_qty')
    def _onchange_qty_booking(self):
        for line in self:
            line.qty_booking = line.product_uom_qty

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for record in self:
            record.product_template_id = record.product_id.product_tmpl_id

    @api.onchange('order_id.is_booking', 'price_unit', 'product_id')
    def _onchange_is_booking(self):
        for line in self:
            if line.product_id:
                price = line.product_id.lst_price
                if line.order_id.is_booking:
                    line.price_unit = price * 1.1
                else:
                    line.price_unit = price

        # config booking order, check max booking
        @api.constrains('qty_booking')
        def _check_max_booking_order(self):
            for line in self:
                config = self.env['booking.order.config'].search([], limit=1)
                if config and line.qty_booking > config.max_booking_order:
                    raise ValidationError(
                        _('Quantity cannot exceed the maximum booking order of %s') % config.max_booking_order)

    # update quantity product if edit
    def write(self, vals):
        for line in self:
            if 'product_uom_qty' in vals:
                product = line.product_id
                new_qty = vals['product_uom_qty']
                qty_difference = new_qty - line.product_uom_qty
                if qty_difference > 0 and product.qty_available < qty_difference:
                    raise ValidationError(_('Not Enough quantity Available for Product %s') % product.display_name)
                product.qty_available -= qty_difference
        return super(SaleOrderLine, self).write(vals)

    # add product if product unlink(delete)
    def unlink(self):
        for line in self:
            if line.product_id:
                if line.order_id.is_booking:
                    product = line.product_id
                    product.qty_available += line.product_uom_qty
        return super(SaleOrderLine, self).unlink()
