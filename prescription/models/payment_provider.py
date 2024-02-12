# -*- coding: utf-8 -*-


from odoo import fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    so_reference_type = fields.Selection(string='Communication',
        selection=[
            ('so_name', 'Based on Document Reference'),
            ('partner', 'Based on Customer ID')], default='so_name',
        help='You can set here the communication type that will appear on prescription orders.'
             'The communication will be given to the customer when they choose the payment method.')