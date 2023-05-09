# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InactiveReason(models.Model):
    _name = "podiatry.inactive.reason"
    _description = "Inactive Reason"
    _order = "sequence"

    sequence = fields.Integer("Sequence", default=10)
    name = fields.Char(string="Reason", required=True, translate=True)

    def _get_default_inactive_reasons(self):
        return {
            'fired': self.env.ref('podiatry.inactive_fired', False),
            'resigned': self.env.ref('podiatry.inactive_resigned', False),
            'retired': self.env.ref('podiatry.inactive_retired', False),
        }

    @api.ondelete(at_uninstall=False)
    def _unlink_except_default_inactive_reasons(self):
        ids = set(map(lambda a: a.id, self._get_default_inactive_reasons().values()))
        if set(self.ids) & ids:
            raise UserError(_('Default inactive reasons cannot be deleted.'))
