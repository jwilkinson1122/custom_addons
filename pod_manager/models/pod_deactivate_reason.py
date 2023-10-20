# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DepartureReason(models.Model):
    _name = "pod.deactivate.reason"
    _description = "Departure Reason"
    _order = "sequence"

    sequence = fields.Integer("Sequence", default=10)
    name = fields.Char(string="Reason", required=True, translate=True)

    def _get_default_deactivate_reasons(self):
        return {
            'moved': self.env.ref('pod_manager.deactivate_moved', False),
            'resigned': self.env.ref('pod_manager.deactivate_resigned', False),
            'retired': self.env.ref('pod_manager.deactivate_retired', False),
        }

    @api.ondelete(at_uninstall=False)
    def _unlink_except_default_deactivate_reasons(self):
        ids = set(map(lambda a: a.id, self._get_default_deactivate_reasons().values()))
        if set(self.ids) & ids:
            raise UserError(_('Default deactivate reasons cannot be deleted.'))
