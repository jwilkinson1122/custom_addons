# -*- coding: utf-8 -*-


from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    company_sign = fields.Text('Signature')

class UserApiKey(models.Model):
    _inherit = 'res.users.apikeys'

    company_sign = fields.Text('Signature ')