# -*- coding: utf-8 -*-


from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.tools import format_datetime
from odoo.exceptions import AccessError, ValidationError


class PrescriptionConfirmation(models.Model):
    _name = 'prescription.confirmation'
    _description = 'Prescription Confirmation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # prescription
    prescription_id = fields.Many2one(
        'prescription.prescription', string='Prescription', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    prescription_device_id = fields.Many2one(
        'prescription.prescription.device', string='Prescription Device', readonly=True, ondelete='restrict',
        states={'draft': [('readonly', False)]})
    active = fields.Boolean(default=True)
    # utm informations
    utm_campaign_id = fields.Many2one('utm.campaign', 'Campaign',  index=True, ondelete='set null')
    utm_source_id = fields.Many2one('utm.source', 'Source', index=True, ondelete='set null')
    utm_medium_id = fields.Many2one('utm.medium', 'Medium', index=True, ondelete='set null')
    # attendee
    partner_id = fields.Many2one(
        'res.partner', string='Booked by',
        states={'done': [('readonly', True)]})
    name = fields.Char(
        string='Attendee Name', index=True,
        compute='_compute_name', readonly=False, store=True, tracking=10)
    email = fields.Char(string='Email', compute='_compute_email', readonly=False, store=True, tracking=11)
    phone = fields.Char(string='Phone', compute='_compute_phone', readonly=False, store=True, tracking=12)
    mobile = fields.Char(string='Mobile', compute='_compute_mobile', readonly=False, store=True, tracking=13)
    # organization
    date_open = fields.Datetime(string='Confirmation Date', readonly=True, default=lambda self: fields.Datetime.now())  # weird crash is directly now
    date_closed = fields.Datetime(
        string='Attended Date', compute='_compute_date_closed',
        readonly=False, store=True)
    prescription_begin_date = fields.Datetime(string="Prescription Start Date", related='prescription_id.date_begin', readonly=True)
    prescription_end_date = fields.Datetime(string="Prescription Complete Date", related='prescription_id.date_end', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', related='prescription_id.company_id',
        store=True, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('open', 'Confirmed'), ('done', 'Attended')],
        string='Status', default='draft', readonly=True, copy=False, tracking=True)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """ Keep an explicit onchange on partner_id. Rationale : if user explicitly
        changes the partner in interface, he want to update the whole customer
        information. If partner_id is updated in code (e.g. updating your personal
        information after having registered in website_prescription_sale) fields with a
        value should not be reset as we don't know which one is the right one.

        In other words
          * computed fields based on partner_id should only update missing
            information. Indeed automated code cannot decide which information
            is more accurate;
          * interface should allow to update all customer related information
            at once. We consider prescription users really want to update all fields
            related to the partner;
        """
        for confirmation in self:
            if confirmation.partner_id:
                confirmation.update(confirmation._synchronize_partner_values(confirmation.partner_id))

    @api.depends('partner_id')
    def _compute_name(self):
        for confirmation in self:
            if not confirmation.name and confirmation.partner_id:
                confirmation.name = confirmation._synchronize_partner_values(
                    confirmation.partner_id,
                    fnames=['name']
                ).get('name') or False

    @api.depends('partner_id')
    def _compute_email(self):
        for confirmation in self:
            if not confirmation.email and confirmation.partner_id:
                confirmation.email = confirmation._synchronize_partner_values(
                    confirmation.partner_id,
                    fnames=['email']
                ).get('email') or False

    @api.depends('partner_id')
    def _compute_phone(self):
        for confirmation in self:
            if not confirmation.phone and confirmation.partner_id:
                confirmation.phone = confirmation._synchronize_partner_values(
                    confirmation.partner_id,
                    fnames=['phone']
                ).get('phone') or False

    @api.depends('partner_id')
    def _compute_mobile(self):
        for confirmation in self:
            if not confirmation.mobile and confirmation.partner_id:
                confirmation.mobile = confirmation._synchronize_partner_values(
                    confirmation.partner_id,
                    fnames=['mobile']
                ).get('mobile') or False

    @api.depends('state')
    def _compute_date_closed(self):
        for confirmation in self:
            if not confirmation.date_closed:
                if confirmation.state == 'done':
                    confirmation.date_closed = fields.Datetime.now()
                else:
                    confirmation.date_closed = False

    @api.constrains('prescription_id', 'state')
    def _check_seats_limit(self):
        for confirmation in self:
            if confirmation.prescription_id.seats_limited and confirmation.prescription_id.seats_max and confirmation.prescription_id.seats_available < (1 if confirmation.state == 'draft' else 0):
                raise ValidationError(_('No more seats available for this prescription.'))

    @api.constrains('prescription_device_id', 'state')
    def _check_device_seats_limit(self):
        for record in self:
            if record.prescription_device_id.seats_max and record.prescription_device_id.seats_available < 0:
                raise ValidationError(_('No more available seats for this device'))

    @api.constrains('prescription_id', 'prescription_device_id')
    def _check_prescription_device(self):
        if any(confirmation.prescription_id != confirmation.prescription_device_id.prescription_id for confirmation in self if confirmation.prescription_device_id):
            raise ValidationError(_('Invalid prescription / device choice'))

    def _synchronize_partner_values(self, partner, fnames=None):
        if fnames is None:
            fnames = ['name', 'email', 'phone', 'mobile']
        if partner:
            contact_id = partner.address_get().get('contact', False)
            if contact_id:
                contact = self.env['res.partner'].browse(contact_id)
                return dict((fname, contact[fname]) for fname in fnames if contact[fname])
        return {}

    # ------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        confirmations = super(PrescriptionConfirmation, self).create(vals_list)

        # auto_confirm if possible; if not automatically confirmed, call mail schedulers in case
        # some were created already open
        if confirmations._check_auto_confirmation():
            confirmations.sudo().action_confirm()
        elif not self.env.context.get('install_mode', False):
            # running the scheduler for demo data can cause an issue where wkhtmltopdf runs during
            # server start and hangs indefinitely, leading to serious crashes
            # we currently avoid this by not running the scheduler, would be best to find the actual
            # reason for this issue and fix it so we can remove this check
            confirmations._update_mail_schedulers()

        return confirmations

    def write(self, vals):
        pre_draft = self.env['prescription.confirmation']
        if vals.get('state') == 'open':
            pre_draft = self.filtered(lambda confirmation: confirmation.state == 'draft')

        ret = super(PrescriptionConfirmation, self).write(vals)

        if vals.get('state') == 'open' and not self.env.context.get('install_mode', False):
            # running the scheduler for demo data can cause an issue where wkhtmltopdf runs during
            # server start and hangs indefinitely, leading to serious crashes
            # we currently avoid this by not running the scheduler, would be best to find the actual
            # reason for this issue and fix it so we can remove this check
            pre_draft._update_mail_schedulers()

        return ret

    def name_get(self):
        """ Custom name_get implementation to better differentiate confirmations
        linked to a given partner but with different name (one partner buying
        several confirmations)

          * name, partner_id has no name -> take name
          * partner_id has name, name void or same -> take partner name
          * both have name: partner + name
        """
        ret_list = []
        for confirmation in self:
            if confirmation.partner_id.name:
                if confirmation.name and confirmation.name != confirmation.partner_id.name:
                    name = '%s, %s' % (confirmation.partner_id.name, confirmation.name)
                else:
                    name = confirmation.partner_id.name
            else:
                name = confirmation.name
            ret_list.append((confirmation.id, name))
        return ret_list

    def _check_auto_confirmation(self):
        if any(not confirmation.prescription_id.auto_confirm or
               (not confirmation.prescription_id.seats_available and confirmation.prescription_id.seats_limited) for confirmation in self):
            return False
        return True

    # ------------------------------------------------------------
    # ACTIONS / BUSINESS
    # ------------------------------------------------------------

    def action_set_draft(self):
        self.write({'state': 'draft'})

    def action_confirm(self):
        self.write({'state': 'open'})

    def action_set_done(self):
        """ Close Confirmation """
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_send_badge_email(self):
        """ Open a window to compose an email, with the template - 'prescription_badge'
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('prescription.prescription_confirmation_mail_template_badge', raise_if_not_found=False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='prescription.confirmation',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id,
            default_composition_mode='comment',
            custom_layout="mail.mail_notification_light",
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def _update_mail_schedulers(self):
        """ Update schedulers to set them as running again, and cron to be called
        as soon as possible. """
        open_confirmations = self.filtered(lambda confirmation: confirmation.state == 'open')
        if not open_confirmations:
            return

        onsubscribe_schedulers = self.env['prescription.mail'].sudo().search([
            ('prescription_id', 'in', open_confirmations.prescription_id.ids),
            ('interval_type', '=', 'after_sub')
        ])
        if not onsubscribe_schedulers:
            return

        onsubscribe_schedulers.update({'mail_done': False})
        # we could simply call _create_missing_mail_confirmations and let cron do their job
        # but it currently leads to several delays. We therefore call execute until
        # cron triggers are correctly used
        onsubscribe_schedulers.with_user(SUPERUSER_ID).execute()

    # ------------------------------------------------------------
    # MAILING / GATEWAY
    # ------------------------------------------------------------

    def _message_get_suggested_recipients(self):
        recipients = super(PrescriptionConfirmation, self)._message_get_suggested_recipients()
        public_users = self.env['res.users'].sudo()
        public_groups = self.env.ref("base.group_public", raise_if_not_found=False)
        if public_groups:
            public_users = public_groups.sudo().with_context(active_test=False).mapped("users")
        try:
            for attendee in self:
                is_public = attendee.sudo().with_context(active_test=False).partner_id.user_ids in public_users if public_users else False
                if attendee.partner_id and not is_public:
                    attendee._message_add_suggested_recipient(recipients, partner=attendee.partner_id, reason=_('Customer'))
                elif attendee.email:
                    attendee._message_add_suggested_recipient(recipients, email=attendee.email, reason=_('Customer Email'))
        except AccessError:     # no read access rights -> ignore suggested recipients
            pass
        return recipients

    def _message_get_default_recipients(self):
        # Prioritize confirmation email over partner_id, which may be shared when a single
        # partner booked multiple seats
        return {r.id: {
            'partner_ids': [],
            'email_to': r.email,
            'email_cc': False}
            for r in self}

    def _message_post_after_hook(self, message, msg_vals):
        if self.email and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.email)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email', '=', new_partner.email),
                    ('state', 'not in', ['cancel']),
                ]).write({'partner_id': new_partner.id})
        return super(PrescriptionConfirmation, self)._message_post_after_hook(message, msg_vals)

    # ------------------------------------------------------------
    # TOOLS
    # ------------------------------------------------------------

    def get_date_range_str(self):
        self.ensure_one()
        today = fields.Datetime.now()
        prescription_date = self.prescription_begin_date
        diff = (prescription_date.date() - today.date())
        if diff.days <= 0:
            return _('today')
        elif diff.days == 1:
            return _('tomorrow')
        elif (diff.days < 7):
            return _('in %d days') % (diff.days, )
        elif (diff.days < 14):
            return _('next week')
        elif prescription_date.month == (today + relativedelta(months=+1)).month:
            return _('next month')
        else:
            return _('on %(date)s', date=format_datetime(self.env, self.prescription_begin_date, tz=self.prescription_id.date_tz, dt_format='medium'))

    def _get_confirmation_summary(self):
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
            'partner_id': self.partner_id.id,
            'device_name': self.prescription_device_id.name or _('None'),
            'prescription_id': self.prescription_id.id,
            'prescription_display_name': self.prescription_id.display_name,
            'company_name': self.prescription_id.company_id and self.prescription_id.company_id.name or False,
        }
