

from odoo import fields, models


class MgmtsystemNonconformityOrigin(models.Model):

    _inherit = "mgmtsystem.nonconformity.origin"

    from_encounter = fields.Boolean()

    responsible_user_id = fields.Many2one("res.users", string="Default Responsible")
    manager_user_id = fields.Many2one("res.users", string="Default Manager")
    notify_creator = fields.Boolean(string="Notify Creator")
