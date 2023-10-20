# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        """Inherit Method to create partner of group practitioner or doctor."""
        vals.update({"partner_id": False})
        res = super(ResPartner, self).create(vals)
        if self._context.get("practitioner_create", False):
            practitioner_group_ids = [
                self.env.ref("podiatry.group_podiatry_practitioner").id,
                self.env.ref("base.group_user").id,
                self.env.ref("base.group_partner_manager").id,
            ]
            res.write(
                {
                    "groups_id": [(6, 0, practitioner_group_ids)],
                    "company_id": self._context.get("practice_id"),
                    "company_ids": [(4, self._context.get("practice_id"))],
                }
            )
        return res
