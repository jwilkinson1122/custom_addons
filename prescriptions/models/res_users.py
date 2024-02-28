

from odoo import models


class Users(models.Model):
    _name = 'res.users'
    _inherit = ['res.users']

    def _init_messaging(self):
        res = super()._init_messaging()
        res['hasPrescriptionsUserGroup'] = self.env.user.has_group('prescriptions.group_prescriptions_user')
        return res
