# -*- coding: utf-8 -*-


import logging
import pytz

from odoo import _, api, Command, fields, models
from odoo.addons.base.models.res_partner import _tz_get
from odoo.tools import format_datetime, is_html_empty
from odoo.exceptions import ValidationError
from odoo.tools.translate import html_translate

_logger = logging.getLogger(__name__)

try:
    import vobject
except ImportError:
    _logger.warning("`vobject` Python module not found, iCal file generation disabled. Consider installing this module if you want to generate iCal files")
    vobject = None


class PrescriptionType(models.Model):
    _name = 'prescription.type'
    _description = 'Prescription Template'
    _order = 'sequence, id'

    def _default_prescription_mail_type_ids(self):
        return [(0, 0,
                 {'notification_type': 'mail',
                  'interval_nbr': 0,
                  'interval_unit': 'now',
                  'interval_type': 'after_sub',
                  'template_ref': 'mail.template, %i' % self.env.ref('prescription.prescription_subscription').id,
                 }),
                (0, 0,
                 {'notification_type': 'mail',
                  'interval_nbr': 1,
                  'interval_unit': 'hours',
                  'interval_type': 'before_prescription',
                  'template_ref': 'mail.template, %i' % self.env.ref('prescription.prescription_reminder').id,
                 }),
                (0, 0,
                 {'notification_type': 'mail',
                  'interval_nbr': 3,
                  'interval_unit': 'days',
                  'interval_type': 'before_prescription',
                  'template_ref': 'mail.template, %i' % self.env.ref('prescription.prescription_reminder').id,
                 })]

    name = fields.Char('Prescription Template', required=True, translate=True)
    note = fields.Html(string='Note')
    sequence = fields.Integer()
    # tickets
    prescription_type_ticket_ids = fields.One2many('prescription.type.ticket', 'prescription_type_id', string='Tickets')
    tag_ids = fields.Many2many('prescription.tag', string="Tags")
    # registration
    has_seats_limitation = fields.Boolean('Limited Seats')
    seats_max = fields.Integer(
        'Maximum Registrations', compute='_compute_default_registration',
        readonly=False, store=True,
        help="It will select this default maximum value when you choose this prescription")
    auto_confirm = fields.Boolean(
        'Automatically Confirm Registrations', default=True,
        help="Prescriptions and registrations will automatically be confirmed "
             "upon creation, easing the flow for simple prescriptions.")
    default_timezone = fields.Selection(
        _tz_get, string='Timezone', default=lambda self: self.env.user.tz or 'UTC')
    # communication
    prescription_type_mail_ids = fields.One2many(
        'prescription.type.mail', 'prescription_type_id', string='Mail Schedule',
        default=_default_prescription_mail_type_ids)
    # ticket reports
    ticket_instructions = fields.Html('Ticket Instructions', translate=True,
        help="This information will be printed on your tickets.")

    @api.depends('has_seats_limitation')
    def _compute_default_registration(self):
        for template in self:
            if not template.has_seats_limitation:
                template.seats_max = 0


class PrescriptionPrescription(models.Model):
    """Prescription"""
    _name = 'prescription.prescription'
    _description = 'Prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_begin'

    def _get_default_stage_id(self):
        return self.env['prescription.stage'].search([], limit=1)

    def _default_description(self):
        # avoid template branding with rendering_bundle=True
        return self.env['ir.ui.view'].with_context(rendering_bundle=True) \
            ._render_template('prescription.prescription_default_descripton')

    def _default_prescription_mail_ids(self):
        return self.env['prescription.type']._default_prescription_mail_type_ids()

    name = fields.Char(string='Prescription', translate=True, required=True)
    note = fields.Html(string='Note', store=True, compute="_compute_note", readonly=False)
    description = fields.Html(string='Description', translate=html_translate, sanitize_attributes=False, sanitize_form=False, default=_default_description)
    active = fields.Boolean(default=True)
    user_id = fields.Many2one('res.users', string='Responsible', tracking=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', change_default=True, default=lambda self: self.env.company, required=False)
    organizer_id = fields.Many2one('res.partner', string='Organizer', tracking=True, default=lambda self: self.env.company.partner_id, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    practice_id = fields.Many2one(
        comodel_name='podiatry.practice', string='Practice')

    practice_name = fields.Char(
        string='Practitioner', related='practice_id.name')

    practitioner_id = fields.Many2one(
        comodel_name='podiatry.practitioner', string='Practitioner')

    practitioner_name = fields.Char(
        string='Practitioner', related='practitioner_id.name')

    practitioner_phone = fields.Char(
        string='Phone', related='practitioner_id.phone')

    practitioner_email = fields.Char(
        string='Email', related='practitioner_id.email')

    patient_id = fields.Many2one(
        comodel_name='podiatry.patient', string='Patient')

    patient_name = fields.Char(
        string='Practitioner', related='patient_id.name')


    prescription_type_id = fields.Many2one('prescription.type', string='Template', ondelete='set null')
    prescription_mail_ids = fields.One2many(
        'prescription.mail', 'prescription_id', string='Mail Schedule', copy=True,
        compute='_compute_prescription_mail_ids', readonly=False, store=True)
    tag_ids = fields.Many2many(
        'prescription.tag', string="Tags", readonly=False,
        store=True, compute="_compute_tag_ids")
    # Kanban fields
    kanban_state = fields.Selection([('normal', 'In Progress'), ('done', 'Done'), ('blocked', 'Blocked')], default='normal', copy=False)
    kanban_state_label = fields.Char(
        string='Kanban State Label', compute='_compute_kanban_state_label',
        store=True, tracking=True)
    stage_id = fields.Many2one(
        'prescription.stage', ondelete='restrict', default=_get_default_stage_id,
        group_expand='_read_group_stage_ids', tracking=True, copy=False)
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True)
    # Seats and computation
    seats_max = fields.Integer(
        string='Maximum Attendees Number',
        compute='_compute_seats_max', readonly=False, store=True,
        help="For each prescription you can define a maximum registration of seats(number of attendees), above this numbers the registrations are not accepted.")
    seats_limited = fields.Boolean('Maximum Attendees', required=True, compute='_compute_seats_limited',
                                   readonly=False, store=True)
    seats_reserved = fields.Integer(
        string='Reserved Seats',
        store=True, readonly=True, compute='_compute_seats')
    seats_available = fields.Integer(
        string='Available Seats',
        store=True, readonly=True, compute='_compute_seats')
    seats_unconfirmed = fields.Integer(
        string='Unconfirmed Seat Reservations',
        store=True, readonly=True, compute='_compute_seats')
    seats_used = fields.Integer(
        string='Number of Participants',
        store=True, readonly=True, compute='_compute_seats')
    seats_expected = fields.Integer(
        string='Number of Expected Attendees',
        compute_sudo=True, readonly=True, compute='_compute_seats_expected')
    # Registration fields
    auto_confirm = fields.Boolean(
        string='Autoconfirmation', compute='_compute_auto_confirm', readonly=False, store=True,
        help='Autoconfirm Registrations. Registrations will automatically be confirmed upon creation.')
    registration_ids = fields.One2many('prescription.registration', 'prescription_id', string='Attendees')
    prescription_ticket_ids = fields.One2many(
        'prescription.prescription.ticket', 'prescription_id', string='Prescription Ticket', copy=True,
        compute='_compute_prescription_ticket_ids', readonly=False, store=True)
    prescription_registrations_started = fields.Boolean(
        'Registrations started', compute='_compute_prescription_registrations_started',
        help="registrations have started if the current datetime is after the earliest starting date of tickets."
    )
    prescription_registrations_open = fields.Boolean(
        'Registration open', compute='_compute_prescription_registrations_open', compute_sudo=True,
        help="Registrations are open if:\n"
        "- the prescription is not ended\n"
        "- there are seats available on prescription\n"
        "- the tickets are sellable (if ticketing is used)")
    prescription_registrations_sold_out = fields.Boolean(
        'Sold Out', compute='_compute_prescription_registrations_sold_out', compute_sudo=True,
        help='The prescription is sold out if no more seats are available on prescription. If ticketing is used and all tickets are sold out, the prescription will be sold out.')
    start_sale_datetime = fields.Datetime(
        'Start sale date', compute='_compute_start_sale_date',
        help='If ticketing is used, contains the earliest starting sale date of tickets.')

    # Date fields
    date_tz = fields.Selection(
        _tz_get, string='Timezone', required=True,
        compute='_compute_date_tz', readonly=False, store=True)
    date_begin = fields.Datetime(string='Start Date', required=True, tracking=True)
    date_end = fields.Datetime(string='End Date', required=True, tracking=True)
    date_begin_located = fields.Char(string='Start Date Located', compute='_compute_date_begin_tz')
    date_end_located = fields.Char(string='End Date Located', compute='_compute_date_end_tz')
    is_ongoing = fields.Boolean('Is Ongoing', compute='_compute_is_ongoing', search='_search_is_ongoing')
    is_one_day = fields.Boolean(compute='_compute_field_is_one_day')
    is_finished = fields.Boolean(compute='_compute_is_finished', search='_search_is_finished')
    # Location and communication
    address_id = fields.Many2one(
        'res.partner', string='Venue', default=lambda self: self.env.company.partner_id.id,
        tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    country_id = fields.Many2one(
        'res.country', 'Country', related='address_id.country_id', readonly=False, store=True)
    # ticket reports
    ticket_instructions = fields.Html('Ticket Instructions', translate=True,
        compute='_compute_ticket_instructions', store=True, readonly=False,
        help="This information will be printed on your tickets.")

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for prescription in self:
            if prescription.kanban_state == 'normal':
                prescription.kanban_state_label = prescription.stage_id.legend_normal
            elif prescription.kanban_state == 'blocked':
                prescription.kanban_state_label = prescription.stage_id.legend_blocked
            else:
                prescription.kanban_state_label = prescription.stage_id.legend_done

    @api.depends('seats_max', 'registration_ids.state')
    def _compute_seats(self):
        """ Determine reserved, available, reserved but unconfirmed and used seats. """
        # initialize fields to 0
        for prescription in self:
            prescription.seats_unconfirmed = prescription.seats_reserved = prescription.seats_used = prescription.seats_available = 0
        # aggregate registrations by prescription and by state
        state_field = {
            'draft': 'seats_unconfirmed',
            'open': 'seats_reserved',
            'done': 'seats_used',
        }
        base_vals = dict((fname, 0) for fname in state_field.values())
        results = dict((prescription_id, dict(base_vals)) for prescription_id in self.ids)
        if self.ids:
            query = """ SELECT prescription_id, state, count(prescription_id)
                        FROM prescription_registration
                        WHERE prescription_id IN %s AND state IN ('draft', 'open', 'done')
                        GROUP BY prescription_id, state
                    """
            self.env['prescription.registration'].flush(['prescription_id', 'state'])
            self._cr.execute(query, (tuple(self.ids),))
            res = self._cr.fetchall()
            for prescription_id, state, num in res:
                results[prescription_id][state_field[state]] = num

        # compute seats_available
        for prescription in self:
            prescription.update(results.get(prescription._origin.id or prescription.id, base_vals))
            if prescription.seats_max > 0:
                prescription.seats_available = prescription.seats_max - (prescription.seats_reserved + prescription.seats_used)

    @api.depends('seats_unconfirmed', 'seats_reserved', 'seats_used')
    def _compute_seats_expected(self):
        for prescription in self:
            prescription.seats_expected = prescription.seats_unconfirmed + prescription.seats_reserved + prescription.seats_used

    @api.depends('date_tz', 'start_sale_datetime')
    def _compute_prescription_registrations_started(self):
        for prescription in self:
            prescription = prescription._set_tz_context()
            if prescription.start_sale_datetime:
                current_datetime = fields.Datetime.context_timestamp(prescription, fields.Datetime.now())
                start_sale_datetime = fields.Datetime.context_timestamp(prescription, prescription.start_sale_datetime)
                prescription.prescription_registrations_started = (current_datetime >= start_sale_datetime)
            else:
                prescription.prescription_registrations_started = True

    @api.depends('date_tz', 'prescription_registrations_started', 'date_end', 'seats_available', 'seats_limited', 'prescription_ticket_ids.sale_available')
    def _compute_prescription_registrations_open(self):
        """ Compute whether people may take registrations for this prescription

          * prescription.date_end -> if prescription is done, registrations are not open anymore;
          * prescription.start_sale_datetime -> lowest start date of tickets (if any; start_sale_datetime
            is False if no ticket are defined, see _compute_start_sale_date);
          * any ticket is available for sale (seats available) if any;
          * seats are unlimited or seats are available;
        """
        for prescription in self:
            prescription = prescription._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(prescription, fields.Datetime.now())
            date_end_tz = prescription.date_end.astimezone(pytz.timezone(prescription.date_tz or 'UTC')) if prescription.date_end else False
            prescription.prescription_registrations_open = prescription.prescription_registrations_started and \
                (date_end_tz >= current_datetime if date_end_tz else True) and \
                (not prescription.seats_limited or prescription.seats_available) and \
                (not prescription.prescription_ticket_ids or any(ticket.sale_available for ticket in prescription.prescription_ticket_ids))

    @api.depends('prescription_ticket_ids.start_sale_datetime')
    def _compute_start_sale_date(self):
        """ Compute the start sale date of an prescription. Currently lowest starting sale
        date of tickets if they are used, of False. """
        for prescription in self:
            start_dates = [ticket.start_sale_datetime for ticket in prescription.prescription_ticket_ids if not ticket.is_expired]
            prescription.start_sale_datetime = min(start_dates) if start_dates and all(start_dates) else False

    @api.depends('prescription_ticket_ids.sale_available')
    def _compute_prescription_registrations_sold_out(self):
        for prescription in self:
            if prescription.seats_limited and not prescription.seats_available:
                prescription.prescription_registrations_sold_out = True
            elif prescription.prescription_ticket_ids:
                prescription.prescription_registrations_sold_out = not any(
                    ticket.seats_available > 0 if ticket.seats_limited else True for ticket in prescription.prescription_ticket_ids
                )
            else:
                prescription.prescription_registrations_sold_out = False

    @api.depends('date_tz', 'date_begin')
    def _compute_date_begin_tz(self):
        for prescription in self:
            if prescription.date_begin:
                prescription.date_begin_located = format_datetime(
                    self.env, prescription.date_begin, tz=prescription.date_tz, dt_format='medium')
            else:
                prescription.date_begin_located = False

    @api.depends('date_tz', 'date_end')
    def _compute_date_end_tz(self):
        for prescription in self:
            if prescription.date_end:
                prescription.date_end_located = format_datetime(
                    self.env, prescription.date_end, tz=prescription.date_tz, dt_format='medium')
            else:
                prescription.date_end_located = False

    @api.depends('date_begin', 'date_end')
    def _compute_is_ongoing(self):
        now = fields.Datetime.now()
        for prescription in self:
            prescription.is_ongoing = prescription.date_begin <= now < prescription.date_end

    def _search_is_ongoing(self, operator, value):
        if operator not in ['=', '!=']:
            raise ValueError(_('This operator is not supported'))
        if not isinstance(value, bool):
            raise ValueError(_('Value should be True or False (not %s)'), value)
        now = fields.Datetime.now()
        if (operator == '=' and value) or (operator == '!=' and not value):
            domain = [('date_begin', '<=', now), ('date_end', '>', now)]
        else:
            domain = ['|', ('date_begin', '>', now), ('date_end', '<=', now)]
        prescription_ids = self.env['prescription.prescription']._search(domain)
        return [('id', 'in', prescription_ids)]

    @api.depends('date_begin', 'date_end', 'date_tz')
    def _compute_field_is_one_day(self):
        for prescription in self:
            # Need to localize because it could begin late and finish early in
            # another timezone
            prescription = prescription._set_tz_context()
            begin_tz = fields.Datetime.context_timestamp(prescription, prescription.date_begin)
            end_tz = fields.Datetime.context_timestamp(prescription, prescription.date_end)
            prescription.is_one_day = (begin_tz.date() == end_tz.date())

    @api.depends('date_end')
    def _compute_is_finished(self):
        for prescription in self:
            if not prescription.date_end:
                prescription.is_finished = False
                continue
            prescription = prescription._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(prescription, fields.Datetime.now())
            datetime_end = fields.Datetime.context_timestamp(prescription, prescription.date_end)
            prescription.is_finished = datetime_end <= current_datetime

    def _search_is_finished(self, operator, value):
        if operator not in ['=', '!=']:
            raise ValueError(_('This operator is not supported'))
        if not isinstance(value, bool):
            raise ValueError(_('Value should be True or False (not %s)'), value)
        now = fields.Datetime.now()
        if (operator == '=' and value) or (operator == '!=' and not value):
            domain = [('date_end', '<=', now)]
        else:
            domain = [('date_end', '>', now)]
        prescription_ids = self.env['prescription.prescription']._search(domain)
        return [('id', 'in', prescription_ids)]

    @api.depends('prescription_type_id')
    def _compute_date_tz(self):
        for prescription in self:
            if prescription.prescription_type_id.default_timezone:
                prescription.date_tz = prescription.prescription_type_id.default_timezone
            if not prescription.date_tz:
                prescription.date_tz = self.env.user.tz or 'UTC'


    @api.onchange('practice_id')
    def onchange_practice_id(self):
        for rec in self:
            return {'domain': {'practitioner_id': [('practice_id', '=', rec.practice_id.id)]}}

    @api.onchange('practitioner_id')
    def onchange_practitioner_id(self):
        for rec in self:
            return {'domain': {'patient_id': [('practitioner_id', '=', rec.practitioner_id.id)]}}

    # seats
    @api.depends('prescription_type_id')
    def _compute_seats_max(self):
        """ Update prescription configuration from its prescription type. Depends are set only
        on prescription_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if prescription type is changed, update prescription configuration. Changing
        prescription type content itself should not trigger this method. """
        for prescription in self:
            if not prescription.prescription_type_id:
                prescription.seats_max = prescription.seats_max or 0
            else:
                prescription.seats_max = prescription.prescription_type_id.seats_max or 0

    @api.depends('prescription_type_id')
    def _compute_seats_limited(self):
        """ Update prescription configuration from its prescription type. Depends are set only
        on prescription_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if prescription type is changed, update prescription configuration. Changing
        prescription type content itself should not trigger this method. """
        for prescription in self:
            if prescription.prescription_type_id.has_seats_limitation != prescription.seats_limited:
                prescription.seats_limited = prescription.prescription_type_id.has_seats_limitation
            if not prescription.seats_limited:
                prescription.seats_limited = False

    @api.depends('prescription_type_id')
    def _compute_auto_confirm(self):
        """ Update prescription configuration from its prescription type. Depends are set only
        on prescription_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if prescription type is changed, update prescription configuration. Changing
        prescription type content itself should not trigger this method. """
        for prescription in self:
            prescription.auto_confirm = prescription.prescription_type_id.auto_confirm

    @api.depends('prescription_type_id')
    def _compute_prescription_mail_ids(self):
        """ Update prescription configuration from its prescription type. Depends are set only
        on prescription_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if prescription type is changed, update prescription configuration. Changing
        prescription type content itself should not trigger this method.

        When synchronizing mails:

          * lines that are not sent and have no registrations linked are remove;
          * type lines are added;
        """
        for prescription in self:
            if not prescription.prescription_type_id and not prescription.prescription_mail_ids:
                prescription.prescription_mail_ids = self._default_prescription_mail_ids()
                continue

            # lines to keep: those with already sent emails or registrations
            mails_to_remove = prescription.prescription_mail_ids.filtered(
                lambda mail: not(mail._origin.mail_done) and not(mail._origin.mail_registration_ids)
            )
            command = [Command.unlink(mail.id) for mail in mails_to_remove]
            if prescription.prescription_type_id.prescription_type_mail_ids:
                command += [
                    Command.create(line._prepare_prescription_mail_values())
                    for line in prescription.prescription_type_id.prescription_type_mail_ids
                ]
            if command:
                prescription.prescription_mail_ids = command

    @api.depends('prescription_type_id')
    def _compute_tag_ids(self):
        """ Update prescription configuration from its prescription type. Depends are set only
        on prescription_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if prescription type is changed, update prescription configuration. Changing
        prescription type content itself should not trigger this method. """
        for prescription in self:
            if not prescription.tag_ids and prescription.prescription_type_id.tag_ids:
                prescription.tag_ids = prescription.prescription_type_id.tag_ids

    @api.depends('prescription_type_id')
    def _compute_prescription_ticket_ids(self):
        """ Update prescription configuration from its prescription type. Depends are set only
        on prescription_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if prescription type is changed, update prescription configuration. Changing
        prescription type content itself should not trigger this method.

        When synchronizing tickets:

          * lines that have no registrations linked are remove;
          * type lines are added;

        Note that updating prescription_ticket_ids triggers _compute_start_sale_date
        (start_sale_datetime computation) so ensure result to avoid cache miss.
        """
        for prescription in self:
            if not prescription.prescription_type_id and not prescription.prescription_ticket_ids:
                prescription.prescription_ticket_ids = False
                continue

            # lines to keep: those with existing registrations
            tickets_to_remove = prescription.prescription_ticket_ids.filtered(lambda ticket: not ticket._origin.registration_ids)
            command = [Command.unlink(ticket.id) for ticket in tickets_to_remove]
            if prescription.prescription_type_id.prescription_type_ticket_ids:
                command += [
                    Command.create({
                        attribute_name: line[attribute_name] if not isinstance(line[attribute_name], models.BaseModel) else line[attribute_name].id
                        for attribute_name in self.env['prescription.type.ticket']._get_prescription_ticket_fields_whitelist()
                    }) for line in prescription.prescription_type_id.prescription_type_ticket_ids
                ]
            prescription.prescription_ticket_ids = command

    @api.depends('prescription_type_id')
    def _compute_note(self):
        for prescription in self:
            if prescription.prescription_type_id and not is_html_empty(prescription.prescription_type_id.note):
                prescription.note = prescription.prescription_type_id.note

    @api.depends('prescription_type_id')
    def _compute_ticket_instructions(self):
        for prescription in self:
            if is_html_empty(prescription.ticket_instructions) and not \
               is_html_empty(prescription.prescription_type_id.ticket_instructions):
                prescription.ticket_instructions = prescription.prescription_type_id.ticket_instructions

    @api.constrains('seats_max', 'seats_available', 'seats_limited')
    def _check_seats_limit(self):
        if any(prescription.seats_limited and prescription.seats_max and prescription.seats_available < 0 for prescription in self):
            raise ValidationError(_('No more available seats.'))

    @api.constrains('date_begin', 'date_end')
    def _check_closing_date(self):
        for prescription in self:
            if prescription.date_end < prescription.date_begin:
                raise ValidationError(_('The closing date cannot be earlier than the beginning date.'))

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['prescription.stage'].search([])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Temporary fix for ``seats_limited`` and ``date_tz`` required fields
            vals.update(self._sync_required_computed(vals))

        prescriptions = super(PrescriptionPrescription, self).create(vals_list)
        for res in prescriptions:
            if res.organizer_id:
                res.message_subscribe([res.organizer_id.id])
        prescriptions.flush()
        return prescriptions

    def write(self, vals):
        if 'stage_id' in vals and 'kanban_state' not in vals:
            # reset kanban state when changing stage
            vals['kanban_state'] = 'normal'
        res = super(PrescriptionPrescription, self).write(vals)
        if vals.get('organizer_id'):
            self.message_subscribe([vals['organizer_id']])
        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_("%s (copy)") % (self.name))
        return super(PrescriptionPrescription, self).copy(default)

    @api.model
    def _get_mail_message_access(self, res_ids, operation, model_name=None):
        if (
            operation == 'create'
            and self.env.user.has_group('prescription.group_prescription_registration_desk')
            and (not model_name or model_name == 'prescription.prescription')
        ):
            # allow the registration desk users to post messages on Prescription
            # can not be done with "_mail_post_access" otherwise public user will be
            # able to post on published Prescription (see website_prescription)
            return 'read'
        return super(PrescriptionPrescription, self)._get_mail_message_access(res_ids, operation, model_name)

    def _sync_required_computed(self, values):
        # TODO: See if the change to seats_limited affects this ?
        """ Call compute fields in cache to find missing values for required fields
        (seats_limited and date_tz) in case they are not given in values """
        missing_fields = list(set(['seats_limited', 'date_tz']).difference(set(values.keys())))
        if missing_fields and values:
            cache_prescription = self.new(values)
            cache_prescription._compute_seats_limited()
            cache_prescription._compute_date_tz()
            return dict((fname, cache_prescription[fname]) for fname in missing_fields)
        else:
            return {}

    def _set_tz_context(self):
        self.ensure_one()
        return self.with_context(tz=self.date_tz or 'UTC')

    def action_set_done(self):
        """
        Action which will move the prescriptions
        into the first next (by sequence) stage defined as "Ended"
        (if they are not already in an ended stage)
        """
        first_ended_stage = self.env['prescription.stage'].search([('pipe_end', '=', True)], limit=1, order='sequence')
        if first_ended_stage:
            self.write({'stage_id': first_ended_stage.id})

    def mail_attendees(self, template_id, force_send=False, filter_func=lambda self: self.state != 'cancel'):
        for prescription in self:
            for attendee in prescription.registration_ids.filtered(filter_func):
                self.env['mail.template'].browse(template_id).send_mail(attendee.id, force_send=force_send)

    def _get_ics_file(self):
        """ Returns iCalendar file for the prescription invitation.
            :returns a dict of .ics file content for each prescription
        """
        result = {}
        if not vobject:
            return result

        for prescription in self:
            cal = vobject.iCalendar()
            cal_prescription = cal.add('vprescription')

            cal_prescription.add('created').value = fields.Datetime.now().replace(tzinfo=pytz.timezone('UTC'))
            cal_prescription.add('dtstart').value = fields.Datetime.from_string(prescription.date_begin).replace(tzinfo=pytz.timezone('UTC'))
            cal_prescription.add('dtend').value = fields.Datetime.from_string(prescription.date_end).replace(tzinfo=pytz.timezone('UTC'))
            cal_prescription.add('summary').value = prescription.name
            if prescription.address_id:
                cal_prescription.add('location').value = prescription.sudo().address_id.contact_address

            result[prescription.id] = cal.serialize().encode('utf-8')
        return result

    @api.autovacuum
    def _gc_mark_prescriptions_done(self):
        """ move every ended prescriptions in the next 'ended stage' """
        ended_prescriptions = self.env['prescription.prescription'].search([
            ('date_end', '<', fields.Datetime.now()),
            ('stage_id.pipe_end', '=', False),
        ])
        if ended_prescriptions:
            ended_prescriptions.action_set_done()
