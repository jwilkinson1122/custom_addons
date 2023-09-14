from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    base_comment_template_ids = fields.Many2many(
        comodel_name="base.comment.template",
        relation="base_comment_template_res_partner_rel",
        column1="res_partner_id",
        column2="base_comment_template_id",
        string="Comment Templates",
        help="Specific partner comments that can be included in reports",
    )

    @api.model
    def _commercial_fields(self):
        """Add comment templates to commercial fields"""
        return super()._commercial_fields() + ["base_comment_template_ids"]
