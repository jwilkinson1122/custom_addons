# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("practice_ids")
    def _compute_practice_count(self):
        for rec in self:
            rec.practice_count = len(rec.practice_ids)

    practice_ids = fields.One2many(
        "practice", "partner_id", string="Practices")
    practice_count = fields.Integer(
        compute=_compute_practice_count, string="Number of Practices", store=True
    )

    def action_view_practices(self):
        xmlid = "practice.action_practice"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        if self.practice_count > 1:
            action["domain"] = [("id", "in", self.practice_ids.ids)]
        else:
            action["views"] = [
                (self.env.ref("practice.view_practice_form").id, "form")]
            action["res_id"] = self.practice_ids and self.practice_ids.ids[0] or False
        return action
