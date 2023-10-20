# -*- coding: utf-8 -*-

import pytz
from datetime import datetime, time
from dateutil.rrule import rrule, DAILY
from random import choice
from string import digits
from werkzeug.urls import url_encode
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.osv.query import Query
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.osv import expression
from odoo.tools.misc import format_date


class PodPractitionerPrivate(models.Model):
    """
    NB: Any field only available on the model pod.practitioner (i.e. not on the
    pod.practitioner.public model) should have `groups="pod_manager.group_pod_user"` on its
    definition to avoid being prefetched when the user hasn't access to the
    pod.practitioner model. Indeed, the prefetch loads the data for all the fields
    that are available according to the group defined on them.
    """
    _name = "pod.practitioner"
    _description = "Practitioner"
    _order = 'name'
    _inherit = ['pod.practitioner.base', 'mail.thread', 'mail.activity.mixin', 'resource.mixin', 'avatar.mixin']
    _mail_post_access = 'read'

    # resource and user
    # required on the resource, make sure required="True" set in the view
    name = fields.Char(string="Practitioner Name", related='resource_id.name', store=True, readonly=False, tracking=True)
    user_id = fields.Many2one('res.users', 'User', related='resource_id.user_id', store=True, readonly=False)
    user_partner_id = fields.Many2one(related='user_id.partner_id', related_sudo=False, string="User's partner")
    active = fields.Boolean('Active', related='resource_id.active', default=True, store=True, readonly=False)
    company_id = fields.Many2one('res.company',required=True)
    company_country_id = fields.Many2one('res.country', 'Company Country', related='company_id.country_id', readonly=True)
    company_country_code = fields.Char(related='company_country_id.code', readonly=True)
    # private partner
    private_address_id = fields.Many2one(
        'res.partner', 'Address', help='Enter here the private address of the practitioner, not the one linked to your company.',
        groups="pod_manager.group_pod_user", tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    is_private_address_a_company = fields.Boolean(
        'The practitioner address has a company linked',
        compute='_compute_is_private_address_a_company',
    )
    private_email = fields.Char(related='private_address_id.email', string="Private Email", groups="pod_manager.group_pod_user")
    lang = fields.Selection(related='private_address_id.lang', string="Lang", groups="pod_manager.group_pod_user", readonly=False)
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', groups="pod_manager.group_pod_user", tracking=True)
    identification_id = fields.Char(string='Identification No', groups="pod_manager.group_pod_user", tracking=True)
    id_number = fields.Binary(string="ID Copy", groups="pod_manager.group_pod_user")
    additional_note = fields.Text(string='Additional Note', groups="pod_manager.group_pod_user", tracking=True)
    specialty_field = fields.Char("Field of Specialty", groups="pod_manager.group_pod_user", tracking=True)
    secondary_contact = fields.Char("Secondary Contact", groups="pod_manager.group_pod_user", tracking=True)
    secondary_phone = fields.Char("Secondary Phone", groups="pod_manager.group_pod_user", tracking=True)

    role_id = fields.Many2one(tracking=True)
    phone = fields.Char(related='private_address_id.phone', related_sudo=False, readonly=False, string="Private Phone", groups="pod_manager.group_pod_user")
    # practitioner in company
    child_ids = fields.One2many('pod.practitioner', 'parent_id', string='Direct subordinates')
    category_ids = fields.Many2many(
        'pod.practitioner.category', 'practitioner_category_rel',
        'emp_id', 'category_id', groups="pod_manager.group_pod_manager",
        string='Tags')
    # misc
    notes = fields.Text('Notes', groups="pod_manager.group_pod_user")
    color = fields.Integer('Color Index', default=0)
    barcode = fields.Char(string="Badge ID", help="ID used for practitioner identification.", groups="pod_manager.group_pod_user", copy=False)
    pin = fields.Char(string="PIN", groups="pod_manager.group_pod_user", copy=False,
        help="PIN used to Check In/Out in the Kiosk Mode of the Attendance application (if enabled in Configuration) and to change the cashier in the Point of Sale application.")
    deactivate_reason_id = fields.Many2one("pod.deactivate.reason", string="Departure Reason", groups="pod_manager.group_pod_user",
                                          copy=False, tracking=True, ondelete='restrict')
    deactivate_description = fields.Html(string="Additional Information", groups="pod_manager.group_pod_user", copy=False, tracking=True)
    deactivate_date = fields.Date(string="Departure Date", groups="pod_manager.group_pod_user", copy=False, tracking=True)
    message_main_attachment_id = fields.Many2one(groups="pod_manager.group_pod_user")
    

    _sql_constraints = [
        ('barcode_uniq', 'unique (barcode)', "The Badge ID must be unique, this one is already assigned to another practitioner."),
        ('user_uniq', 'unique (user_id, company_id)', "A user cannot be linked to multiple practitioners in the same company.")
    ]

    @api.depends('name', 'user_id.avatar_1920', 'image_1920')
    def _compute_avatar_1920(self):
        super()._compute_avatar_1920()

    @api.depends('name', 'user_id.avatar_1024', 'image_1024')
    def _compute_avatar_1024(self):
        super()._compute_avatar_1024()

    @api.depends('name', 'user_id.avatar_512', 'image_512')
    def _compute_avatar_512(self):
        super()._compute_avatar_512()

    @api.depends('name', 'user_id.avatar_256', 'image_256')
    def _compute_avatar_256(self):
        super()._compute_avatar_256()

    @api.depends('name', 'user_id.avatar_128', 'image_128')
    def _compute_avatar_128(self):
        super()._compute_avatar_128()

    def _compute_avatar(self, avatar_field, image_field):
        for practitioner in self:
            avatar = practitioner._origin[image_field]
            if not avatar:
                if practitioner.user_id:
                    avatar = practitioner.user_id[avatar_field]
                else:
                    avatar = practitioner._avatar_get_placeholder()
            practitioner[avatar_field] = avatar

    def name_get(self):
        if self.check_access_rights('read', raise_exception=False):
            return super(PodPractitionerPrivate, self).name_get()
        return self.env['pod.practitioner.public'].browse(self.ids).name_get()

    def _read(self, fields):
        if self.check_access_rights('read', raise_exception=False):
            return super(PodPractitionerPrivate, self)._read(fields)

        res = self.env['pod.practitioner.public'].browse(self.ids).read(fields)
        for r in res:
            record = self.browse(r['id'])
            record._update_cache({k:v for k,v in r.items() if k in fields}, validate=False)

    def read(self, fields, load='_classic_read'):
        if self.check_access_rights('read', raise_exception=False):
            return super(PodPractitionerPrivate, self).read(fields, load=load)
        private_fields = set(fields).difference(self.env['pod.practitioner.public']._fields.keys())
        if private_fields:
            raise AccessError(_('The fields "%s" you try to read is not available on the public practitioner profile.') % (','.join(private_fields)))
        return self.env['pod.practitioner.public'].browse(self.ids).read(fields, load=load)

    @api.model
    def load_views(self, views, options=None):
        if self.check_access_rights('read', raise_exception=False):
            return super(PodPractitionerPrivate, self).load_views(views, options=options)
        return self.env['pod.practitioner.public'].load_views(views, options=options)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
            We override the _search because it is the method that checks the access rights
            This is correct to override the _search. That way we enforce the fact that calling
            search on an pod.practitioner returns a pod.practitioner recordset, even if you don't have access
            to this model, as the result of _search (the ids of the public practitioners) is to be
            browsed on the pod.practitioner model. This can be trusted as the ids of the public
            practitioners exactly match the ids of the related pod.practitioner.
        """
        if self.check_access_rights('read', raise_exception=False):
            return super(PodPractitionerPrivate, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        try:
            ids = self.env['pod.practitioner.public']._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        except ValueError:
            raise AccessError(_('You do not have access to this document.'))
        if not count and isinstance(ids, Query):
            # the result is expected from this table, so we should link tables
            ids = super(PodPractitionerPrivate, self.sudo())._search([('id', 'in', ids)])
        return ids

    def get_formview_id(self, access_uid=None):
        """ Override this method in order to redirect many2one towards the right model depending on access_uid """
        if access_uid:
            self_sudo = self.with_user(access_uid)
        else:
            self_sudo = self

        if self_sudo.check_access_rights('read', raise_exception=False):
            return super(PodPractitionerPrivate, self).get_formview_id(access_uid=access_uid)
        # Hardcode the form view for public practitioner
        return self.env.ref('pod_manager.pod_practitioner_public_view_form').id

    def get_formview_action(self, access_uid=None):
        """ Override this method in order to redirect many2one towards the right model depending on access_uid """
        res = super(PodPractitionerPrivate, self).get_formview_action(access_uid=access_uid)
        if access_uid:
            self_sudo = self.with_user(access_uid)
        else:
            self_sudo = self

        if not self_sudo.check_access_rights('read', raise_exception=False):
            res['res_model'] = 'pod.practitioner.public'

        return res

    @api.constrains('pin')
    def _verify_pin(self):
        for practitioner in self:
            if practitioner.pin and not practitioner.pin.isdigit():
                raise ValidationError(_("The PIN must be a sequence of digits."))

    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id:
            self.update(self._sync_user(self.user_id, (bool(self.image_1920))))
            if not self.name:
                self.name = self.user_id.name

    @api.onchange('resource_calendar_id')
    def _onchange_timezone(self):
        if self.resource_calendar_id and not self.tz:
            self.tz = self.resource_calendar_id.tz

    def _sync_user(self, user, practitioner_has_image=False):
        vals = dict(
            practice_email=user.email,
            user_id=user.id,
        )
        if not practitioner_has_image:
            vals['image_1920'] = user.image_1920
        if user.tz:
            vals['tz'] = user.tz
        return vals

    @api.model
    def create(self, vals):
        if vals.get('user_id'):
            user = self.env['res.users'].browse(vals['user_id'])
            vals.update(self._sync_user(user, bool(vals.get('image_1920'))))
            vals['name'] = vals.get('name', user.name)
        practitioner = super(PodPractitionerPrivate, self).create(vals)
        if practitioner.practice_id:
            self.env['mail.channel'].sudo().search([
                ('subscription_practice_ids', 'in', practitioner.practice_id.id)
            ])._subscribe_users_automatically()
        # Launch onboarding plans
        url = '/web#%s' % url_encode({
            'action': 'pod.plan_wizard_action',
            'active_id': practitioner.id,
            'active_model': 'pod.practitioner',
            'menu_id': self.env.ref('pod_manager.menu_pod_root').id,
        })
        practitioner._message_log(body=_('<b>Congratulations!</b> May I recommend you to setup an <a href="%s">onboarding plan?</a>') % (url))
        return practitioner

    def write(self, vals):
        if vals.get('user_id'):
            # Update the profile pictures with user, except if provided 
            vals.update(self._sync_user(self.env['res.users'].browse(vals['user_id']),
                                        (bool(self.image_1920))))
        res = super(PodPractitionerPrivate, self).write(vals)
        if vals.get('practice_id') or vals.get('user_id'):
            practice_id = vals['practice_id'] if vals.get('practice_id') else self[:1].practice_id.id
            # When added to a practice or changing user, subscribe to the channels auto-subscribed by practice
            self.env['mail.channel'].sudo().search([
                ('subscription_practice_ids', 'in', practice_id)
            ])._subscribe_users_automatically()
        return res

    def unlink(self):
        resources = self.mapped('resource_id')
        super(PodPractitionerPrivate, self).unlink()
        return resources.unlink()

    def _get_practitioner_m2o_to_empty_on_archived_practitioners(self):
        return ['parent_id', 'assistant_id']

    def _get_user_m2o_to_empty_on_archived_practitioners(self):
        return []

    def toggle_active(self):
        res = super(PodPractitionerPrivate, self).toggle_active()
        unarchived_practitioners = self.filtered(lambda practitioner: practitioner.active)
        unarchived_practitioners.write({
            'deactivate_reason_id': False,
            'deactivate_description': False,
            'deactivate_date': False
        })
        archived_addresses = unarchived_practitioners.mapped('private_address_id').filtered(lambda addr: not addr.active)
        archived_addresses.toggle_active()

        archived_practitioners = self.filtered(lambda e: not e.active)
        if archived_practitioners:
            # Empty links to this practitioners (example: manager, assistant, time off responsible, ...)
            practitioner_fields_to_empty = self._get_practitioner_m2o_to_empty_on_archived_practitioners()
            user_fields_to_empty = self._get_user_m2o_to_empty_on_archived_practitioners()
            practitioner_domain = [[(field, 'in', archived_practitioners.ids)] for field in practitioner_fields_to_empty]
            user_domain = [[(field, 'in', archived_practitioners.user_id.ids) for field in user_fields_to_empty]]
            practitioners = self.env['pod.practitioner'].search(expression.OR(practitioner_domain + user_domain))
            for practitioner in practitioners:
                for field in practitioner_fields_to_empty:
                    if practitioner[field] in archived_practitioners:
                        practitioner[field] = False
                for field in user_fields_to_empty:
                    if practitioner[field] in archived_practitioners.user_id:
                        practitioner[field] = False

        if len(self) == 1 and not self.active and not self.env.context.get('no_wizard', False):
            return {
                'type': 'ir.actions.act_window',
                'name': _('Register Departure'),
                'res_model': 'pod.deactivate.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'active_id': self.id},
                'views': [[False, 'form']]
            }
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self._origin:
            return {'warning': {
                'title': _("Warning"),
                'message': _("To avoid multi company issues (loosing the access to your previous contracts, leaves, ...), you should create another practitioner in the new company instead.")
            }}

    def generate_random_barcode(self):
        for practitioner in self:
            practitioner.barcode = '041'+"".join(choice(digits) for i in range(9))

    @api.depends('private_address_id.parent_id')
    def _compute_is_private_address_a_company(self):
        """Checks that chosen address (res.partner) is not linked to a company.
        """
        for practitioner in self:
            try:
                practitioner.is_private_address_a_company = practitioner.private_address_id.parent_id.id is not False
            except AccessError:
                practitioner.is_private_address_a_company = False

    def _get_tz(self):
        # Finds the first valid timezone in his tz, his work hours tz,
        #  the company calendar tz or UTC and returns it as a string
        self.ensure_one()
        return self.tz or\
               self.resource_calendar_id.tz or\
               self.company_id.resource_calendar_id.tz or\
               'UTC'

    def _get_tz_batch(self):
        # Finds the first valid timezone in his tz, his work hours tz,
        #  the company calendar tz or UTC
        # Returns a dict {practitioner_id: tz}
        return {emp.id: emp._get_tz() for emp in self}

    # ---------------------------------------------------------
    # Business Methods
    # ---------------------------------------------------------

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Practitioners'),
            'template': '/pod_manager/static/xls/pod_practitioner.xls'
        }]

    def _post_author(self):
        """
        When a user updates his own practitioner's data, all operations are performed
        by super user. However, tracking messages should not be posted as OdooBot
        but as the actual user.
        This method is used in the overrides of `_message_log` and `message_post`
        to post messages as the correct user.
        """
        real_user = self.env.context.get('binary_field_real_user')
        if self.env.is_superuser() and real_user:
            self = self.with_user(real_user)
        return self

    def _get_unusual_days(self, date_from, date_to=None):
        # Checking the calendar directly allows to not grey out the leaves taken
        # by the practitioner
        # Prevents a traceback when loading calendar views and no practitioner is linked to the user.
        if not self:
            return {}
        self.ensure_one()
        calendar = self.resource_calendar_id
        if not calendar:
            return {}
        dfrom = datetime.combine(fields.Date.from_string(date_from), time.min).replace(tzinfo=pytz.UTC)
        dto = datetime.combine(fields.Date.from_string(date_to), time.max).replace(tzinfo=pytz.UTC)

        works = {d[0].date() for d in calendar._work_intervals_batch(dfrom, dto)[False]}
        return {fields.Date.to_string(day.date()): (day.date() not in works) for day in rrule(DAILY, dfrom, until=dto)}

    # ---------------------------------------------------------
    # Messaging
    # ---------------------------------------------------------

    def _message_log(self, **kwargs):
        return super(PodPractitionerPrivate, self._post_author())._message_log(**kwargs)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        return super(PodPractitionerPrivate, self._post_author()).message_post(**kwargs)

    def _sms_get_partner_fields(self):
        return ['user_partner_id']

    def _sms_get_number_fields(self):
        return ['mobile_phone']

