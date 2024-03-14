from odoo import _, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    instructions_count = fields.Integer(
        compute="_compute_instructions_count", string="# Instructions"
    )

    def _compute_instructions_count(self):
        # do just one query for all records
        data = self.env["product.set"].read_group(
            self._instruction_domain(), ["partner_id"], ["partner_id"]
        )
        data_mapped = {
            count["partner_id"][0]: count["partner_id_count"] for count in data
        }
        for rec in self:
            rec.instructions_count = data_mapped.get(rec.id, 0)

    def _instruction_domain(self):
        return [("partner_id", "in", self.ids), ("typology", "=", "instruction")]

    def action_view_instructions(self):
        self.ensure_one()
        xmlid = "pod_product_set.act_open_product_set_view"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action.update(
            {
                "name": _("Instructions"),
                "domain": self._instruction_domain(),
                "context": {
                    "default_typology": "instruction",
                    "default_partner_id": self.id,
                },
            }
        )
        return action
