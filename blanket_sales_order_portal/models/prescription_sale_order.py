# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models

class Prescription(models.Model):
    _inherit = 'prescription'

    def _compute_access_url(self):
        super(Prescription, self)._compute_access_url()
        for bso in self:
            bso.access_url = '/web/portal/prescription/view/%s' % bso.id