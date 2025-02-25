from odoo import fields, models


class ContactRole(models.Model):
    _name = "contact.role"
    _description = "Contact Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
    # color = fields.Integer(string="Color")
    color = fields.Integer(string="Color Index", default=0)
    # parent_id = fields.Many2one(
    #     "contact.role", string="Parent Role", help="Parent role for hierarchy."
    # )
    # child_ids = fields.One2many(
    #     "contact.role",
    #     "parent_id",
    #     string="Child Roles",
    #     help="Sub-roles under this role.",
    # )

    # partners = fields.Many2many(
    #     "res.partner",
    #     "contact_role_res_partner_rel",
    #     "role_id",
    #     "partner_id",
    #     string="Partners",
    # )

    # def name_get(self):
    #     result = []
    #     for role in self:
    #         display_name = (
    #             f"{role.name} ({role.description})" if role.description else role.name
    #         )
    #         result.append((role.id, display_name))
    #     return result
