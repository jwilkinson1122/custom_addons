from lxml import etree
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.depends('groups_id')
    def _compute_share(self):
        super()._compute_share()
        for user in self.filtered_domain([("is_user_profile", "=", True)]):
            user.share = True

    @api.model
    def _get_default_field_ids(self):
        return self.env['ir.model.fields'].sudo().search([
            ('model', 'in', ('res.users', 'res.partner')),
            ('name', 'in', ('action_id', 'menu_id', 'groups_id')),
        ]).ids

    superuser_id = fields.Integer(default=SUPERUSER_ID)
    # is_user_profile = fields.Boolean('Is User Profile')
    is_user_profile = fields.Boolean(
        string="Is User Profile",
        default=False,
        index=True
    )

    user_profile_id = fields.Many2one('res.users', 'User Profile')
    user_ids = fields.One2many(
        'res.users', 'user_profile_id', 'Users',
        domain=[('is_user_profile', '=', False)])
    field_ids = fields.Many2many(
        'ir.model.fields', 'res_users_fields_rel', 'user_id', 'field_id',
        'Fields to update',
        domain=[
            ('model', 'in', ('res.users', 'res.partner')),
            ('ttype', 'not in', ('one2many',)),
            ('name', 'not in', ('is_user_profile', 'user_profile_id',
                                'user_ids', 'field_ids', 'view'))],
        default=_get_default_field_ids)
    is_update_users = fields.Boolean(
        string="Update users after creation", default=lambda *a: True,
        help="If non checked, users associated to this profile "
        "will not be updated after creation")
    users_count = fields.Integer(compute='_compute_users_count')

    role_line_ids = fields.One2many(
        comodel_name="res.users.role.line",
        inverse_name="user_id",
        string="Role lines",
        default=lambda self: self._default_role_lines(),
    )
    
    role_ids = fields.One2many(
        comodel_name="res.users.role",
        string="Roles",
        compute="_compute_role_ids",
        compute_sudo=True,
    )


    # is_user_profile = fields.Boolean(compute='_compute_is_user_profile',readonly=True)

    # @api.depends('is_user_profile')
    # def _compute_is_user_profile(self):
    #     for user in self:
    #         user.is_user_profile = self.env.context.get("is_user_profile", False)

    @api.constrains('is_user_profile', 'user_profile_id')
    def _check_profile_nesting(self):
        for user in self:
            if user.is_user_profile and user.user_profile_id:
                raise ValidationError(_("Profiles cannot inherit from other profiles."))


    @api.model
    def _default_role_lines(self):
        default_user = self.env.ref("base.default_user", raise_if_not_found=False)
        default_values = []
        if default_user:
            for role_line in default_user.with_context(active_test=False).role_line_ids:
                default_values.append(
                    {
                        "role_id": role_line.role_id.id,
                        "date_from": role_line.date_from,
                        "date_to": role_line.date_to,
                        "is_enabled": role_line.is_enabled,
                    }
                )
        return default_values

    @api.depends("role_line_ids.role_id")
    def _compute_role_ids(self):
        for user in self:
            user.role_ids = user.role_line_ids.mapped("role_id")

    @api.constrains('user_profile_id')
    def _check_user_profile_id(self):
        admins = self.env.ref('base.user_root') | \
            self.env.ref('base.user_admin')
        for user in self:
            if user.user_profile_id in admins:
                raise ValidationError(
                    _("You can't use %s as user profile !") %
                    user.user_profile_id.name)

    @api.depends('user_ids')
    def _compute_users_count(self):
        for user in self:
            user.users_count = len(user.user_ids)

    @api.onchange('is_user_profile')
    def onchange_user_profile(self):
        if self.is_user_profile:
            self.active = self.id == SUPERUSER_ID
            self.user_profile_id = False

    def _update_from_profile(self, fields=None):
        """
        Sync allowed fields from the linked user profile.
        Only users sharing the same profile are supported.
        """
        if not self:
            return

        profile_ids = self.mapped("user_profile_id").ids
        if len(profile_ids) != 1:
            raise UserError(_("_update_from_profile only supports users with the same profile."))

        user_profile = self[0].user_profile_id
        if not user_profile:
            return

        allowed_fields = set(user_profile.field_ids.mapped("name"))
        if fields:
            fields = set(fields) & allowed_fields
        else:
            fields = allowed_fields

        if not fields:
            return

        vals = {}
        for field_name in fields:
            value = user_profile[field_name]
            field = self._fields[field_name]
            if field.type == "many2one":
                vals[field_name] = value.id
            elif field.type == "many2many":
                vals[field_name] = [(6, 0, value.ids)]
            # elif field.type == "one2many":
            #     raise UserError(_("_update_from_profile does not support One2many fields."))
            elif field.type == 'one2many':
                continue  # silently skip instead of raising
            else:
                vals[field_name] = value
        
        if vals:
            _logger.info("Updating users %s from profile %s: %s", self.ids, user_profile.id, vals)

            self.with_context(bypass_profile_protection=True).write(vals)

    def _update_users_linked_to_profile(self, fields=None):
        for user_profile in self.filtered(
                lambda user: user.is_user_profile and user.is_update_users):
            user_profile.with_context(active_test=False).mapped(
                'user_ids')._update_from_profile(fields)

    def _generate_profile_login(self, name):
        """
        Generate a dummy login string for profile users based on their name.
        """
        base = name.lower().strip().replace(" ", "_").replace("/", "_")
        return f"profile__{base}"
    
    
    def _is_builtin_admin(self):
        try:
            root = self.env.ref('base.user_root').id
            admin = self.env.ref('base.user_admin').id
            return any(u.id in (root, admin) for u in self)
        except Exception:
            return False

    def _allow_manual_group_toggle(self):
        return (
            self.env.context.get('allow_manual_group_toggle')
            or self._is_builtin_admin()
        )
    
    def _check_protected_user_fields(self, vals):
        if self.env.context.get("bypass_profile_protection") or self._allow_manual_group_toggle():
            return
        # Profile flag (for profile records)
        is_profile_user = vals.get("is_user_profile") or any(u.is_user_profile for u in self)

        # If user_profile_id is being set now, or is already set on the record
        is_profile_linked = vals.get("user_profile_id") or any(u.user_profile_id for u in self)

        protected_fields = {"groups_id", "role_line_ids"}
        touched_fields = protected_fields & vals.keys()

        if touched_fields and not (is_profile_user or is_profile_linked):
            _logger.warning(
                "[User Access Control] BLOCKED attempt to manually set protected fields %s on users %s",
                touched_fields, self.ids or ['(unsaved)']
            )
            raise UserError(
                _("You cannot manually set groups or roles on a user.\nUse a profile or role assignment.")
            )
        elif touched_fields:
            _logger.debug(
                "[User Access Control] Allowing protected field update (%s) because user will be linked to profile %s",
                touched_fields,
                vals.get("user_profile_id") or self.mapped("user_profile_id.id")
            )

    def _strip_protected_group_fields(self, vals):
        if self._allow_manual_group_toggle():
            return  # do nothing; let in_group_* and groups_id pass through
        # Remove all virtual UI group toggles
        virtual_keys = [k for k in vals if k.startswith("in_group_")]
        for k in virtual_keys:
            vals.pop(k)

        # Optionally remove `groups_id` if context does not allow
        if "groups_id" in vals:
            if not (
                self.env.context.get("bypass_profile_protection")
                or vals.get("is_user_profile")
                or vals.get("user_profile_id")
                or any(u.is_user_profile or u.user_profile_id for u in self)
            ):
                _logger.warning(
                    "[User Access Control] Stripping groups_id from vals: %s", vals["groups_id"]
                )
                vals.pop("groups_id")

        if virtual_keys:
            _logger.debug("[User Access Control] Stripped virtual group fields: %s", virtual_keys)


    @api.model_create_multi
    def create(self, vals_list):
        sanitized_vals_list = []

        for vals in vals_list:
            context = dict(self.env.context)

            # Strip virtual group fields like in_group_1, in_group_2, etc.
            self._strip_protected_group_fields(vals)

            # Auto-generate login for profiles if missing
            if vals.get("is_user_profile") and not vals.get("login"):
                temp_user = self.new(vals)
                vals["login"] = temp_user._generate_profile_login(vals.get("name", "profile"))

            # Centralized protection check
            self._check_protected_user_fields(vals)

            if vals.get("is_user_profile"):
                context["from_create_profile"] = True

            self = self.with_context(context)
            sanitized_vals_list.append(vals)

        new_records = super().create(sanitized_vals_list)

        for record, vals in zip(new_records, vals_list):
            if vals.get("user_profile_id"):
                record.with_context(bypass_profile_protection=True)._update_from_profile()

        new_records.sudo().set_groups_from_roles()
        return new_records

    def write(self, vals):

        # Strip virtual group fields like in_group_1, in_group_2, etc.
        self._strip_protected_group_fields(vals)

        
        self._check_protected_user_fields(vals)

        # Auto-generate login if missing for profile
        if "is_user_profile" in vals or any(u.is_user_profile for u in self):
            for user in self.filtered("is_user_profile"):
                if not vals.get("login"):
                    name = vals.get("name", user.name or "profile")
                    vals["login"] = user._generate_profile_login(name)

        # Prevent manual login change on profile (only if it's being changed)
        if not self.env.context.get("bypass_profile_protection"):
            for user in self.filtered("is_user_profile"):
                if "login" in vals and vals["login"] != user.login:
                    raise UserError(
                        _("You cannot manually update the login of a profile. It is generated automatically.")
                    )

        vals = self._remove_reified_groups(vals)

        users_to_update = self.filtered(
            lambda user: vals.get("user_profile_id") and user.user_profile_id.id != vals["user_profile_id"]
        )

        res = super().write(vals)

        if vals.get("user_profile_id"):
            users_to_update.with_context(bypass_profile_protection=True)._update_from_profile()
        else:
            self._update_users_linked_to_profile(list(vals.keys()))

        self.sudo().set_groups_from_roles()
        return res

    @classmethod
    def authenticate(cls, db, login, password, user_agent_env):
        uid = super().authenticate(db, login, password, user_agent_env)
        # On login, ensure the proper roles are applied
        # The last Role applied may not be the correct one,
        # sonce the new session current company can be different
        with cls.pool.cursor() as cr:
            env = api.Environment(cr, uid, {})
            if env.user.role_line_ids:
                env.user.set_groups_from_roles()
        return uid

    def _get_enabled_roles(self):
        """Return enabled role lines, optionally filtered by company context."""
        enabled_roles = self.role_line_ids.filtered(lambda rec: rec.is_enabled)

        if not enabled_roles:
            return super()._get_enabled_roles() if hasattr(super(), "_get_enabled_roles") else enabled_roles

        if self.env.context.get("active_company_ids"):
            company_ids = self.env.context["active_company_ids"]
        else:
            company_ids = self.company_id.ids

        active_roles = self.env["res.users.role.line"]
        for role_line in enabled_roles:
            if not role_line.company_id:
                active_roles |= role_line
            elif role_line.company_id.id in company_ids:
                # Check if this role exists for all companies in context
                matching = enabled_roles.filtered(
                    lambda x, rl=role_line: x.role_id == rl.role_id and x.company_id.id in company_ids
                )
                if len(matching) == len(company_ids):
                    active_roles |= role_line

        return active_roles

    def set_groups_from_roles(self, force=False):
        """Set (replace) the groups following the roles defined on users.
        If no role is defined on the user, its groups are let untouched unless
        the `force` parameter is `True`.
        """
        role_groups = {}
        # We obtain all the groups associated to each role first, so that
        # it is faster to compare later with each user's groups.
        for role in self.mapped("role_line_ids.role_id"):
            role_groups[role] = list(
                set(
                    role.group_id.ids
                    + role.implied_ids.ids
                    + role.trans_implied_ids.ids
                )
            )
        for user in self:
            if not user.role_line_ids and not force:
                continue
            group_ids = []
            for role_line in user._get_enabled_roles():
                role = role_line.role_id
                group_ids += role_groups[role]
            group_ids = list(set(group_ids))  # Remove duplicates IDs
            groups_to_add = list(set(group_ids) - set(user.groups_id.ids))
            groups_to_remove = list(set(user.groups_id.ids) - set(group_ids))
            to_add = [(4, gr) for gr in groups_to_add]
            to_remove = [(3, gr) for gr in groups_to_remove]
            groups = to_remove + to_add
            if groups:
                vals = {"groups_id": groups}
                super(ResUsers, user).write(vals)
        return True

    @api.model
    def _get_user_groups_view(self, groups, readonly=False):
        # call base to get the dynamic fragment
        arch, view = super()._get_user_groups_view(groups, readonly=readonly)
        if self.env.context.get('allow_manual_group_toggle'):
            return arch, view

        # parse and mark all in_group_* fields readonly
        root = etree.fromstring(arch)
        for node in root.xpath(".//field[starts-with(@name, 'in_group_')]"):
            node.set('readonly', '1')
        arch = etree.tostring(root, encoding='unicode')
        return arch, view