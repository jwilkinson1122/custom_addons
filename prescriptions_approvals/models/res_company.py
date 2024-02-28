

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    prescriptions_approvals_settings = fields.Boolean(default=False)
    approvals_folder_id = fields.Many2one('prescriptions.folder', string="Approvals Workspace",
                                          default=lambda self: self.env.ref('prescriptions_approvals.prescriptions_approvals_folder', raise_if_not_found=False),
                                          check_company=True)
    approvals_tag_ids = fields.Many2many('prescriptions.tag', 'approvals_tags_rel')
