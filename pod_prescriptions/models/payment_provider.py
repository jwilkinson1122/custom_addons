# -*- coding: utf-8 -*-


from odoo import fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    rx_reference_type = fields.Selection(string='Communication',
        selection=[
            ('rx_name', 'Based on Document Reference'),
            ('partner', 'Based on Customer ID')], default='rx_name',
        help='You can set here the communication type that will appear on prescriptions orders.'
             'The communication will be given to the customer when they choose the payment method.')
