from odoo import api, fields, models

class IrModel(models.Model):
    _inherit = 'ir.model'

    def _get_first_level_relations(self):
        Fields = self.env['ir.model.fields']
        field_recs = Fields.search([
            ('ttype', 'in', ('many2one', 'one2many', 'many2many')),
            ('model_id', 'in', self.ids),
        ])
        return self.search([('model', 'in', field_recs.mapped('relation'))])

    def _get_relations(self, level=1):
        """
        Return models linked to models given in params
        If you don't want limit the relations level, indicate level = -1
        """
        relations = self
        while self and level:
            self = self._get_first_level_relations() - relations
            relations |= self
            level -= 1
        return self


class ResGroups(models.Model):
    _inherit = "res.groups"


    active = fields.Boolean(default=True)

    view_access = fields.Many2many( groups="base.group_system",
    )

    # The inverse field of the field group_id on the res.users.role model
    # This field should be used a One2one relation as a role can only be
    # represented by one group. It's declared as a One2many field as the
    # inverse field on the res.users.role it's declared as a Many2one
    role_id = fields.One2many( comodel_name="res.users.role", inverse_name="group_id", help="Relation for the groups that represents a role",
    )

    role_ids = fields.Many2many( comodel_name="res.users.role", relation="res_groups_implied_roles_rel", string="Roles", compute="_compute_role_ids", help="Roles in which the group is involved",
    )

    parent_ids = fields.Many2many(
        "res.groups",
        "res_groups_implied_rel",
        "hid",
        "gid", string="Parents", help="Inverse relation for the Inherits field. "
        "The groups from which this group is inheriting",
    )

    trans_parent_ids = fields.Many2many( comodel_name="res.groups", string="Parent Groups", compute="_compute_trans_parent_ids", recursive=True,
    )

    role_count = fields.Integer("# Roles", compute="_compute_role_count")

    def _compute_role_count(self):
        for group in self:
            group.role_count = len(group.role_ids)

    @api.depends("parent_ids.trans_parent_ids")
    def _compute_trans_parent_ids(self):
        for group in self:
            group.trans_parent_ids = (
                group.parent_ids | group.parent_ids.trans_parent_ids
            )

    def _compute_role_ids(self):
        for group in self:
            if group.trans_parent_ids:
                group.role_ids = group.trans_parent_ids.role_id
            else:
                group.role_ids = group.role_id

    def action_view_roles(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_odoo_master.action_res_users_role_tree"
        )
        action["context"] = {}
        if len(self.role_ids) > 1:
            action["domain"] = [("id", "in", self.role_ids.ids)]
        elif self.role_ids:
            form_view = [
                (self.env.ref("pod_odoo_master.view_res_users_role_form").id, "form")
            ]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = self.role_ids.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def _update_users(self, vals):
        if vals.get('users'):
            Users = self.env['res.users']
            user_profiles = Users.browse()
            for item in vals['users']:
                user_ids = []
                if item[0] == 6:
                    user_ids = item[2]
                elif item[0] == 4:
                    user_ids = [item[1]]
                users = Users.browse(user_ids)
                user_profiles |= users.filtered(
                    lambda user: user.is_user_profile)
                user_profiles |= users.mapped('user_profile_id')
            if user_profiles:
                user_profiles._update_users_linked_to_profile()

    def write(self, vals):
        # INFO: it's not useful to override create method because
        # natively ResGroups.create calls ResGroups.write({'users': [...]})
        res = super(ResGroups, self).write(vals)
        self._update_users(vals)
        return res

    def button_complete_access_controls(self):
        """Create access rules for the first level relation models
        # of access rule models not only in readonly"""
        name = ""
        def filter_rule(rule):
            return rule.perm_write or rule.perm_create or rule.perm_unlink
        Access = self.env['ir.model.access']
        for group in self:
            models = group.model_access.filtered(
                filter_rule).mapped('model_id')
            for model in models._get_relations(
                    self._context.get('relations_level', 1)):
                name = '%s %s' % (model.model, group.name)
                if not self.env['ir.model.access'].search([('name', '=', name)]):
                    Access.create({
                        'name': name,
                        'model_id': model.id,
                        'group_id': group.id,
                        'perm_read': True,
                        'perm_write': False,
                        'perm_create': False,
                        'perm_unlink': False,
                    })
        return True
