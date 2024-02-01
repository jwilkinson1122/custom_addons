# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InactiveReason(models.Model):
    _name = "hr.inactive.reason"
    _description = "Inactive Reason"
    _order = "sequence"

    sequence = fields.Integer("Sequence", default=10)
    name = fields.Char(string="Reason", required=True, translate=True)
    reason_code = fields.Integer()

    def _get_default_inactive_reasons(self):
        return {
            'relocate': 342,
            'resigned': 343,
            'retired': 340,
        }

    @api.ondelete(at_uninstall=False)
    def _unlink_except_default_inactive_reasons(self):
        master_inactive_codes = self._get_default_inactive_reasons().values()
        if any(reason.reason_code in master_inactive_codes for reason in self):
            raise UserError(_('Default inactive reasons cannot be deleted.'))
