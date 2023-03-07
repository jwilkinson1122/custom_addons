from openerp.exceptions import ValidationError
from odoo import api, fields, models


class RoomOrder(models.Model):
    _name = 'hotel.room_order'
    _description = 'Room Orders'

    name = fields.Char(string='Order ID', readonly=True,
                       required=True, copy=False, default='New')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hotel.room_order.sequence') or 'New'
        result = super(RoomOrder, self).create(vals)
        return result

    orderroomdetail_ids = fields.One2many(
        comodel_name='hotel.order_room_detail', inverse_name='orderroom_id', string='Room Order')
    orderadditionaldetail_ids = fields.One2many(
        comodel_name='hotel.order_additional_detail', inverse_name='orderadditional_id', string='Additional Order')

    total = fields.Integer(compute='_compute_total',
                           string='Total')

    @api.depends('orderroomdetail_ids', 'orderadditionaldetail_ids')
    def _compute_total(self):
        for record in self:
            a = sum(self.env['hotel.order_room_detail'].search(
                [('orderroom_id', '=', record.id)]).mapped('price'))
            b = sum(self.env['hotel.order_additional_detail'].search(
                [('orderadditional_id', '=', record.id)]).mapped('price'))
            record.total = (a+b) * record.days_count

    is_pay = fields.Boolean(string='Is Pay')
    is_clean = fields.Boolean(string='Is Clean', readonly=True, default=False)

    date_order = fields.Datetime('Order Date', default=fields.Datetime.now())
    date_checkin = fields.Date(
        string='Check In', required=True, default=fields.Datetime.now)
    date_checkout = fields.Date(
        string='Check Out', required=True)

    days_count = fields.Integer(
        string="Days Count", compute='_compute_days_count', readonly=True, store=True)

    @api.depends('date_checkin', 'date_checkout')
    def _compute_days_count(self):
        for record in self:
            if record.date_checkout and record.date_checkin:
                to_date = fields.Datetime.to_datetime(record.date_checkout)
                from_date = fields.Datetime.to_datetime(record.date_checkin)
                record.days_count = int(((to_date - from_date)).days)

    state = fields.Selection(string='State', selection=[(
        'pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('cleaned', 'Cleaned')], default='pending')

    def action_cancel(self):
        self.state = 'cancelled'

    def action_clean(self):
        if self.state == 'completed':
            self.state = 'cleaned'
            self.is_clean = True

    # customer personal information
    cust_name = fields.Char(string='Customer Name')
    phone_num = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')


class OrderRoomDetail(models.Model):
    _name = 'hotel.order_room_detail'
    _description = 'Room Order Detail'

    name = fields.Char(string='Name')
    orderroom_id = fields.Many2one(
        comodel_name='hotel.room_order', string='Order')
    room_id = fields.Many2one(comodel_name='hotel.room', string='Room')
    qty = fields.Integer(string='Quantity', required=True)

    price_per_unit = fields.Integer(
        compute='_compute_price_per_unit', string='Price per Unit')

    @ api.depends('room_id')
    def _compute_price_per_unit(self):
        for record in self:
            record.price_per_unit = record.room_id.price

    price = fields.Integer(compute='_compute_price',
                           string='price', store=True)

    @ api.depends('qty', 'price_per_unit')
    def _compute_price(self):
        for record in self:
            record.price = record.price_per_unit * record.qty

    # Stock check
    @api.constrains('qty')
    def _check_qty(self):
        for record in self:
            isNotEnough = self.env['hotel.room'].search(
                [('stock', '<', record.qty), ('id', '=', record.id)])

            if isNotEnough:
                raise ValidationError("Not Enough Stock!")

    # Decrease room stock
    @api.model
    def create(self, vals):
        record = super(OrderRoomDetail, self).create(vals)
        if record.qty:
            self.env['hotel.room'].search(
                [('id', '=', record.room_id.id)]).write({'stock': record.room_id.stock - record.qty})
            return record


class OrderAdditionalDetail(models.Model):
    _name = 'hotel.order_additional_detail'
    _description = 'Additional Order Detail'

    name = fields.Char(string='Name')
    orderadditional_id = fields.Many2one(
        comodel_name='hotel.room_order', string='Order')
    additional_id = fields.Many2one(
        comodel_name='hotel.additional', string='Additional')
    qty = fields.Integer(string='Quantity', required=True)

    price_per_unit = fields.Integer(
        compute='_compute_price_per_unit', string='Price per Unit')

    @ api.depends('additional_id')
    def _compute_price_per_unit(self):
        for record in self:
            record.price_per_unit = record.additional_id.price

    price = fields.Integer(compute='_compute_price',
                           string='price', store=True)

    @ api.depends('qty', 'price_per_unit')
    def _compute_price(self):
        for record in self:
            record.price = record.price_per_unit * record.qty
