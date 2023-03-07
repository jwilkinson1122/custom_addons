from odoo import api, fields, models


class RoomPayment(models.Model):
    _name = 'hotel.room_payment'
    _description = 'Room Payment'

    room_id = fields.Many2one(
        comodel_name='hotel.room_order', string='Room Order ID')
    name = fields.Char(compute='_compute_customer_name',
                       string='Customer Name')

    @api.depends('room_id')
    def _compute_customer_name(self):
        for record in self:
            record.name = self.env['hotel.room_order'].search(
                [('id', '=', record.room_id.id)]).cust_name

    total = fields.Integer(
        compute='_compute_total_price', string='Total Price')

    @api.depends('room_id')
    def _compute_total_price(self):
        for record in self:
            record.total = record.room_id.total

    payment = fields.Selection(string='Payment Type', selection=[(
        'credit card', 'Credit Card'), ('online payment', 'Online Payment'), ('cash', 'Cash',), ('debit card', 'Debit Card')])

    @api.model
    def create(self, vals):
        record = super(RoomPayment, self).create(vals)
        if record.payment:
            self.env['hotel.room_order'].search(
                [('id', '=', record.room_id.id)]).write({'state': 'completed', 'is_pay': True})
            return record

    # override method
    def unlink(self):
        for i in self:
            self.env['hotel.room_order'].search(
                [('id', '=', i.room_id.id)]).write({'state': 'pending', 'is_pay': False})
        # Return boolean
        record = super(RoomPayment, self).unlink()
