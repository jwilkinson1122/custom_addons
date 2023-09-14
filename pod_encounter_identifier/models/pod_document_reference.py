# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class PodiatryDocumentReference(models.Model):
    _inherit = "pod.document.reference"

    @api.model
    def get_request_format(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("pod.document.reference.identifier")
        )

    @api.model
    def _get_internal_identifier(self, vals):
        code = self._get_nwp_internal_identifier(vals)
        if code:
            return code
        return super()._get_internal_identifier(vals)
