# -*- coding: utf-8 -*-

from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import AccessError


POD_READABLE_FIELDS = [
    'active',
    'child_ids',
    'practitioner_id',
    'private_address_id',
    'practitioner_ids',
    'practitioner_parent_id',
    'pod_existence_state',
    'last_activity',
    'last_activity_time',
    'can_edit',
    'is_system',
]

POD_WRITABLE_FIELDS = [
    'additional_note',
    'private_street',
    'private_street2',
    'private_city',
    'private_state_id',
    'private_zip',
    'private_country_id',
    'address_id',
    'barcode',
    'category_ids',
    'assistant_id',
    'practice_id',
    'display_name',
    'secondary_contact',
    'secondary_phone',
    'practitioner_country_id',
    'identification_id',
    'is_private_address_a_company',
    'role_title',
    'private_email',
    'mobile_phone',
    'notes',
    'practitioner_parent_id',
    'practitioner_phone',
    'pin',
    'practice_email',
    'practice_location_id',
    'practice_phone',
    'specialty_field',
    'private_lang',
    'practitioner_type',
]


class User(models.Model):
    _inherit = ['res.users']

    def _practitioner_ids_domain(self):
        # practitioner_ids is considered a safe field and as such will be fetched as sudo.
        # So try to enforce the security rules on the field to make sure we do not load practitioners outside of active companies
        return [('company_id', 'in', self.env.company.ids + self.env.context.get('allowed_company_ids', []))]

    # note: a user can only be linked to one practitioner per company (see sql constraint in ´pod.practitioner´)
    practitioner_ids = fields.One2many('pod.practitioner', 'user_id', string='Related practitioner', domain=_practitioner_ids_domain)
    practitioner_id = fields.Many2one('pod.practitioner', string="Company practitioner",
        compute='_compute_company_practitioner', search='_search_company_practitioner', store=False)

    role_title = fields.Char(related='practitioner_id.role_title', readonly=False, related_sudo=False)
    practice_phone = fields.Char(related='practitioner_id.practice_phone', readonly=False, related_sudo=False)
    mobile_phone = fields.Char(related='practitioner_id.mobile_phone', readonly=False, related_sudo=False)
    practitioner_phone = fields.Char(related='practitioner_id.phone', readonly=False, related_sudo=False)
    practice_email = fields.Char(related='practitioner_id.practice_email', readonly=False, related_sudo=False)
    category_ids = fields.Many2many(related='practitioner_id.category_ids', string="Practitioner Tags", readonly=False, related_sudo=False)
    practice_id = fields.Many2one(related='practitioner_id.practice_id', readonly=False, related_sudo=False)
    address_id = fields.Many2one(related='practitioner_id.address_id', readonly=False, related_sudo=False)
    practice_location_id = fields.Many2one(related='practitioner_id.practice_location_id', readonly=False, related_sudo=False)
    practitioner_parent_id = fields.Many2one(related='practitioner_id.parent_id', readonly=False, related_sudo=False)
    assistant_id = fields.Many2one(related='practitioner_id.assistant_id', readonly=False, related_sudo=False)
    private_address_id = fields.Many2one(related='practitioner_id.private_address_id', readonly=False, related_sudo=False)
    private_street = fields.Char(related='private_address_id.street', string="Private Street", readonly=False, related_sudo=False)
    private_street2 = fields.Char(related='private_address_id.street2', string="Private Street2", readonly=False, related_sudo=False)
    private_city = fields.Char(related='private_address_id.city', string="Private City", readonly=False, related_sudo=False)
    private_state_id = fields.Many2one(
        related='private_address_id.state_id', string="Private State", readonly=False, related_sudo=False,
        domain="[('country_id', '=?', private_country_id)]")
    private_zip = fields.Char(related='private_address_id.zip', readonly=False, string="Private Zip", related_sudo=False)
    private_country_id = fields.Many2one(related='private_address_id.country_id', string="Private Country", readonly=False, related_sudo=False)
    is_private_address_a_company = fields.Boolean(related='practitioner_id.is_private_address_a_company', readonly=False, related_sudo=False)
    private_email = fields.Char(related='private_address_id.email', string="Private Email", readonly=False)
    private_lang = fields.Selection(related='private_address_id.lang', string="Practitioner Lang", readonly=False)
    practitioner_country_id = fields.Many2one(related='practitioner_id.country_id', string="Practitioner's Country", readonly=False, related_sudo=False)
    identification_id = fields.Char(related='practitioner_id.identification_id', readonly=False, related_sudo=False)
    secondary_contact = fields.Char(related='practitioner_id.secondary_contact', readonly=False, related_sudo=False)
    secondary_phone = fields.Char(related='practitioner_id.secondary_phone', readonly=False, related_sudo=False)
    additional_note = fields.Text(related='practitioner_id.additional_note', readonly=False, related_sudo=False)
    barcode = fields.Char(related='practitioner_id.barcode', readonly=False, related_sudo=False)
    pin = fields.Char(related='practitioner_id.pin', readonly=False, related_sudo=False)
    specialty_field = fields.Char(related='practitioner_id.specialty_field', readonly=False, related_sudo=False)
    practitioner_count = fields.Integer(compute='_compute_practitioner_count')
    pod_existence_state = fields.Selection(related='practitioner_id.pod_existence_state')
    last_activity = fields.Date(related='practitioner_id.last_activity')
    last_activity_time = fields.Char(related='practitioner_id.last_activity_time')
    practitioner_type = fields.Selection(related='practitioner_id.practitioner_type', readonly=False, related_sudo=False)

    can_edit = fields.Boolean(compute='_compute_can_edit')
    is_system = fields.Boolean(compute="_compute_is_system")

    @api.depends_context('uid')
    def _compute_is_system(self):
        self.is_system = self.env.user._is_system()

    def _compute_can_edit(self):
        can_edit = self.env['ir.config_parameter'].sudo().get_param('pod_manager.pod_practitioner_self_edit') or self.env.user.has_group('pod_manager.group_pod_user')
        for user in self:
            user.can_edit = can_edit

    @api.depends('practitioner_ids')
    def _compute_practitioner_count(self):
        for user in self.with_context(active_test=False):
            user.practitioner_count = len(user.practitioner_ids)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + POD_READABLE_FIELDS + POD_WRITABLE_FIELDS

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + POD_WRITABLE_FIELDS

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # When the front-end loads the views it gets the list of available fields
        # for the user (according to its access rights). Later, when the front-end wants to
        # populate the view with data, it only asks to read those available fields.
        # However, in this case, we want the user to be able to read/write its own data,
        # even if they are protected by groups.
        # We make the front-end aware of those fields by sending all field definitions.
        # Note: limit the `sudo` to the only action of "editing own profile" action in order to
        # avoid breaking `groups` mecanism on res.users form view.
        profile_view = self.env.ref("pod_manager.res_users_view_form_profile")
        original_user = self.env.user
        if profile_view and view_id == profile_view.id:
            self = self.with_user(SUPERUSER_ID)
        result = super(User, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        # Due to using the SUPERUSER the result will contain action that the user may not have access too
        # here we filter out actions that requires special implicit rights to avoid having unusable actions
        # in the dropdown menu.
        if toolbar and self.env.user != original_user:
            self = self.with_user(original_user.id)
            if not self.user_has_groups("base.group_erp_manager"):
                change_password_action = self.env.ref("base.change_password_wizard_action")
                result['toolbar']['action'] = [act for act in result['toolbar']['action'] if act['id'] != change_password_action.id]
        return result

    def _get_practitioner_fields_to_sync(self):
        """Get values to sync to the related practitioner when the User is changed.
        """
        return ['name', 'email', 'image_1920', 'tz']

    def write(self, vals):
        """
        Synchronize user and its related practitioner
        and check access rights if practitioners are not allowed to update
        their own data (otherwise sudo is applied for self data).
        """
        pod_fields = {
            field
            for field_name, field in self._fields.items()
            if field.related_field and field.related_field.model_name == 'pod.practitioner' and field_name in vals
        }
        can_edit_self = self.env['ir.config_parameter'].sudo().get_param('pod_manager.pod_practitioner_self_edit') or self.env.user.has_group('pod_manager.group_pod_user')
        if pod_fields and not can_edit_self:
            # Raise meaningful error message
            raise AccessError(_("You are only allowed to update your preferences. Please contact a POD officer to update other information."))

        result = super(User, self).write(vals)

        practitioner_values = {}
        for fname in [f for f in self._get_practitioner_fields_to_sync() if f in vals]:
            practitioner_values[fname] = vals[fname]

        if practitioner_values:
            if 'email' in practitioner_values:
                practitioner_values['practice_email'] = practitioner_values.pop('email')
            if 'image_1920' in vals:
                without_image = self.env['pod.practitioner'].sudo().search([('user_id', 'in', self.ids), ('image_1920', '=', False)])
                with_image = self.env['pod.practitioner'].sudo().search([('user_id', 'in', self.ids), ('image_1920', '!=', False)])
                without_image.write(practitioner_values)
                if not can_edit_self:
                    practitioner_values.pop('image_1920')
                with_image.write(practitioner_values)
            else:
                self.env['pod.practitioner'].sudo().search([('user_id', 'in', self.ids)]).write(practitioner_values)
        return result

    @api.model
    def action_get(self):
        if self.env.user.practitioner_id:
            return self.env['ir.actions.act_window']._for_xml_id('pod_manager.res_users_action_preferences')
        return super(User, self).action_get()

    @api.depends('practitioner_ids')
    @api.depends_context('company')
    def _compute_company_practitioner(self):
        practitioner_per_user = {
            practitioner.user_id: practitioner
            for practitioner in self.env['pod.practitioner'].search([('user_id', 'in', self.ids), ('company_id', '=', self.env.company.id)])
        }
        for user in self:
            user.practitioner_id = practitioner_per_user.get(user)

    def _search_company_practitioner(self, operator, value):
        return [('practitioner_ids', operator, value)]

    def action_create_practitioner(self):
        self.ensure_one()
        self.env['pod.practitioner'].create(dict(
            name=self.name,
            company_id=self.env.company.id,
            **self.env['pod.practitioner']._sync_user(self)
        ))
