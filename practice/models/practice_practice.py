# -*- coding: utf-8 -*-


import logging
import pytz
import time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
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


class PracticeType(models.Model):
    _name = 'practice.type'
    _description = 'Practice Template'
    _order = 'sequence, id'

    def _default_practice_mail_type_ids(self):
        return [(0, 0,
                 {'notification_type': 'mail',
                  'interval_nbr': 0,
                  'interval_unit': 'now',
                  'interval_type': 'after_sub',
                  'template_ref': 'mail.template, %i' % self.env.ref('practice.practice_subscription').id,
                 }),
                (0, 0,
                 {'notification_type': 'mail',
                  'interval_nbr': 1,
                  'interval_unit': 'hours',
                  'interval_type': 'before_practice',
                  'template_ref': 'mail.template, %i' % self.env.ref('practice.practice_reminder').id,
                 }),
                (0, 0,
                 {'notification_type': 'mail',
                  'interval_nbr': 3,
                  'interval_unit': 'days',
                  'interval_type': 'before_practice',
                  'template_ref': 'mail.template, %i' % self.env.ref('practice.practice_reminder').id,
                 })]

    name = fields.Char('Practice Template', required=True, translate=True)
    note = fields.Html(string='Note')
    sequence = fields.Integer()
    # devices
    practice_type_device_ids = fields.One2many('practice.type.device', 'practice_type_id', string='Devices')
    tag_ids = fields.Many2many('practice.tag', string="Tags")
    # confirmation
    has_seats_limitation = fields.Boolean('Limited Seats')
    seats_max = fields.Integer(
        'Maximum Confirmations', compute='_compute_default_confirmation',
        readonly=False, store=True,
        help="It will select this default maximum value when you choose this practice")
    auto_confirm = fields.Boolean(
        'Automatically Confirm Confirmations', default=True,
        help="Practices and confirmations will automatically be confirmed "
             "upon creation, easing the flow for simple practices.")
    default_timezone = fields.Selection(
        _tz_get, string='Timezone', default=lambda self: self.env.user.tz or 'UTC')
    # communication
    practice_type_mail_ids = fields.One2many(
        'practice.type.mail', 'practice_type_id', string='Mail Schedule',
        default=_default_practice_mail_type_ids)
    # device reports
    device_instructions = fields.Html('Practice Instructions', translate=True,
        help="This information will be printed on your devices.")

    @api.depends('has_seats_limitation')
    def _compute_default_confirmation(self):
        for template in self:
            if not template.has_seats_limitation:
                template.seats_max = 0


class PracticePractice(models.Model):
    """Practice"""
    _name = 'practice.practice'
    _description = 'Practice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_begin'
    _rec_name = "name"


    def _get_default_stage_id(self):
        return self.env['practice.stage'].search([], limit=1)

    def _default_description(self):
        # avoid template branding with rendering_bundle=True
        return self.env['ir.ui.view'].with_context(rendering_bundle=True) \
            ._render_template('practice.practice_default_description')

    def _default_practice_mail_ids(self):
        return self.env['practice.type']._default_practice_mail_type_ids()

    # name = fields.Char(string='Practice', translate=True, required=True)
    name = fields.Char(string='Order Reference', required=True, copy=False, index=True, readonly=True, default=lambda self: _('New'))

    note = fields.Html(string='Note', store=True, compute="_compute_note", readonly=False)
    description = fields.Html(string='Description', translate=html_translate, sanitize_attributes=False, sanitize_form=False, default=_default_description)
    active = fields.Boolean(default=True)
    user_id = fields.Many2one('res.users', string='Created by', tracking=True, default=lambda self: self.env.user)
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


    practice_type_id = fields.Many2one('practice.type', string='Template', ondelete='set null')
    practice_mail_ids = fields.One2many(
        'practice.mail', 'practice_id', string='Mail Schedule', copy=True,
        compute='_compute_practice_mail_ids', readonly=False, store=True)
    tag_ids = fields.Many2many(
        'practice.tag', string="Tags", readonly=False,
        store=True, compute="_compute_tag_ids")
    # Kanban fields
    kanban_state = fields.Selection([('normal', 'In Progress'), ('done', 'Done'), ('blocked', 'Blocked')], default='normal', copy=False)
    kanban_state_label = fields.Char(
        string='Kanban State Label', compute='_compute_kanban_state_label',
        store=True, tracking=True)
    stage_id = fields.Many2one(
        'practice.stage', ondelete='restrict', default=_get_default_stage_id,
        group_expand='_read_group_stage_ids', tracking=True, copy=False)
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True)
    # Seats and computation
    seats_max = fields.Integer(
        string='Maximum Attendees Number',
        compute='_compute_seats_max', readonly=False, store=True,
        help="For each practice you can define a maximum confirmation of seats(number of attendees), above this numbers the confirmations are not accepted.")
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
    # Confirmation fields
    auto_confirm = fields.Boolean(
        string='Autoconfirmation', compute='_compute_auto_confirm', readonly=False, store=True,
        help='Autoconfirm Confirmations. Confirmations will automatically be confirmed upon creation.')
    confirmation_ids = fields.One2many('practice.confirmation', 'practice_id', string='Attendees')
    practice_device_ids = fields.One2many(
        'practice.practice.device', 'practice_id', string='Practice Device', copy=True,
        compute='_compute_practice_device_ids', readonly=False, store=True)
    practice_confirmations_started = fields.Boolean(
        'Confirmations started', compute='_compute_practice_confirmations_started',
        help="confirmations have started if the current datetime is after the earliest starting date of devices."
    )
    practice_confirmations_open = fields.Boolean(
        'Confirmation open', compute='_compute_practice_confirmations_open', compute_sudo=True,
        help="Confirmations are open if:\n"
        "- the practice is not ended\n"
        "- there are seats available on practice\n"
        "- the devices are sellable (if deviceing is used)")
    practice_confirmations_sold_out = fields.Boolean(
        'Sold Out', compute='_compute_practice_confirmations_sold_out', compute_sudo=True,
        help='The practice is sold out if no more seats are available on practice. If deviceing is used and all devices are sold out, the practice will be sold out.')
    start_sale_datetime = fields.Datetime(
        'Start sale date', compute='_compute_start_sale_date',
        help='If deviceing is used, contains the earliest starting sale date of devices.')
    
    @api.model
    def _get_begin_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        begin_date = fields.Datetime.context_timestamp(
            self, fields.Datetime.now())
        return fields.Datetime.to_string(begin_date)
    
    @api.model
    def _get_end_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        end_date = fields.Datetime.context_timestamp(
            self, fields.Datetime.now() + timedelta(days=1)
        )
        return fields.Datetime.to_string(end_date)

    # @api.model
    # def _get_hold_date(self):
    #     self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
    #     hold_date = fields.Datetime.context_timestamp(
    #         self, fields.Datetime.now() + timedelta(days=1)
    #     )
    #     return fields.Datetime.to_string(hold_date)
    
    # @api.depends('practitioner_id')
    # def _compute_request_date_onchange(self):
    #     today_date = fields.Date.today()
    #     if self.request_date != today_date:
    #         self.request_date = today_date
    #         return {
    #             "warning": {
    #                 "title": "Changed Request Date",
    #                 "message": "Request date changed to today!",
    #             }
    #         }


    # Date fields
    date_tz = fields.Selection(
        _tz_get, string='Timezone', required=True,
        compute='_compute_date_tz', readonly=False, store=True)
    # date_begin = fields.Datetime(string='Start Date', required=True, tracking=True)
    date_begin = fields.Datetime("Created", required=True, tracking=True, default=_get_begin_date)
    # date_end = fields.Datetime(string='End Date', tracking=True)
    date_end = fields.Datetime("Complete", tracking=True)
    # request_date = fields.Date(default=lambda s: fields.Date.today(), compute="_compute_request_date_onchange", store=True, readonly=False)
    # request_date = fields.Datetime('Requested', copy=False, help="This is the delivery date requested by the customer. "
    #                                        "If set, the delivery order will be scheduled based on "
    #                                        "this date rather than product lead times.")
    expected_date = fields.Datetime("Expected Date", compute='_compute_expected_date', store=False,  # Note: can not be stored since depends on today()
        help="Delivery date you can promise to the customer, computed from the minimum lead time of the order lines.")
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
    # device reports
    device_instructions = fields.Html('Practice Instructions', translate=True,
        compute='_compute_device_instructions', store=True, readonly=False,
        help="This information will be printed on your devices.")
    
    ship_to_patient = fields.Boolean('Ship to Patient')
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)


    # @api.onchange('practitioner_id')
    # def _onchange_practitioner(self):
    #     '''
    #     The purpose of the method is to define a domain for the available
    #     purchase orders.
    #     '''
    #     address_id = self.practitioner_id
    #     self.practitioner_address_id = address_id

    # practitioner_address_id = fields.Many2one(
    #     'res.partner', string="Practitioner Address")
    
    
    # @api.depends('practice_line.customer_lead', 'date_order', 'order_line.state')
    # def _compute_expected_date(self):
    #     """ For service and consumable, we only take the min dates. This method is extended in sale_stock to
    #         take the picking_policy of SO into account.
    #     """
    #     self.mapped("order_line")   
    #     for order in self:
    #         dates_list = []
    #         for line in order.order_line.filtered(lambda x: x.state != 'cancel' and not x._is_delivery() and not x.display_type):
    #             dt = line._expected_date()
    #             dates_list.append(dt)
    #         if dates_list:
    #             order.expected_date = fields.Datetime.to_string(min(dates_list))
    #         else:
    #             order.expected_date = False


    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for practice in self:
            if practice.kanban_state == 'normal':
                practice.kanban_state_label = practice.stage_id.legend_normal
            elif practice.kanban_state == 'blocked':
                practice.kanban_state_label = practice.stage_id.legend_blocked
            else:
                practice.kanban_state_label = practice.stage_id.legend_done

    @api.depends('seats_max', 'confirmation_ids.state')
    def _compute_seats(self):
        """ Determine reserved, available, reserved but unconfirmed and used seats. """
        # initialize fields to 0
        for practice in self:
            practice.seats_unconfirmed = practice.seats_reserved = practice.seats_used = practice.seats_available = 0
        # aggregate confirmations by practice and by state
        state_field = {
            'draft': 'seats_unconfirmed',
            'open': 'seats_reserved',
            'done': 'seats_used',
        }
        base_vals = dict((fname, 0) for fname in state_field.values())
        results = dict((practice_id, dict(base_vals)) for practice_id in self.ids)
        if self.ids:
            query = """ SELECT practice_id, state, count(practice_id)
                        FROM practice_confirmation
                        WHERE practice_id IN %s AND state IN ('draft', 'open', 'done')
                        GROUP BY practice_id, state
                    """
            self.env['practice.confirmation'].flush(['practice_id', 'state'])
            self._cr.execute(query, (tuple(self.ids),))
            res = self._cr.fetchall()
            for practice_id, state, num in res:
                results[practice_id][state_field[state]] = num

        # compute seats_available
        for practice in self:
            practice.update(results.get(practice._origin.id or practice.id, base_vals))
            if practice.seats_max > 0:
                practice.seats_available = practice.seats_max - (practice.seats_reserved + practice.seats_used)

    @api.depends('seats_unconfirmed', 'seats_reserved', 'seats_used')
    def _compute_seats_expected(self):
        for practice in self:
            practice.seats_expected = practice.seats_unconfirmed + practice.seats_reserved + practice.seats_used

    @api.depends('date_tz', 'start_sale_datetime')
    def _compute_practice_confirmations_started(self):
        for practice in self:
            practice = practice._set_tz_context()
            if practice.start_sale_datetime:
                current_datetime = fields.Datetime.context_timestamp(practice, fields.Datetime.now())
                start_sale_datetime = fields.Datetime.context_timestamp(practice, practice.start_sale_datetime)
                practice.practice_confirmations_started = (current_datetime >= start_sale_datetime)
            else:
                practice.practice_confirmations_started = True

    @api.depends('date_tz', 'practice_confirmations_started', 'date_end', 'seats_available', 'seats_limited', 'practice_device_ids.sale_available')
    def _compute_practice_confirmations_open(self):
        """ Compute whether people may take confirmations for this practice

          * practice.date_end -> if practice is done, confirmations are not open anymore;
          * practice.start_sale_datetime -> lowest start date of devices (if any; start_sale_datetime
            is False if no device are defined, see _compute_start_sale_date);
          * any device is available for sale (seats available) if any;
          * seats are unlimited or seats are available;
        """
        for practice in self:
            practice = practice._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(practice, fields.Datetime.now())
            date_end_tz = practice.date_end.astimezone(pytz.timezone(practice.date_tz or 'UTC')) if practice.date_end else False
            practice.practice_confirmations_open = practice.practice_confirmations_started and \
                (date_end_tz >= current_datetime if date_end_tz else True) and \
                (not practice.seats_limited or practice.seats_available) and \
                (not practice.practice_device_ids or any(device.sale_available for device in practice.practice_device_ids))

    @api.depends('practice_device_ids.start_sale_datetime')
    def _compute_start_sale_date(self):
        """ Compute the start sale date of an practice. Currently lowest starting sale
        date of devices if they are used, of False. """
        for practice in self:
            start_dates = [device.start_sale_datetime for device in practice.practice_device_ids if not device.is_expired]
            practice.start_sale_datetime = min(start_dates) if start_dates and all(start_dates) else False

    @api.depends('practice_device_ids.sale_available')
    def _compute_practice_confirmations_sold_out(self):
        for practice in self:
            if practice.seats_limited and not practice.seats_available:
                practice.practice_confirmations_sold_out = True
            elif practice.practice_device_ids:
                practice.practice_confirmations_sold_out = not any(
                    device.seats_available > 0 if device.seats_limited else True for device in practice.practice_device_ids
                )
            else:
                practice.practice_confirmations_sold_out = False

    @api.depends('date_tz', 'date_begin')
    def _compute_date_begin_tz(self):
        for practice in self:
            if practice.date_begin:
                practice.date_begin_located = format_datetime(
                    self.env, practice.date_begin, tz=practice.date_tz, dt_format='medium')
            else:
                practice.date_begin_located = False

    @api.depends('date_tz', 'date_end')
    def _compute_date_end_tz(self):
        for practice in self:
            if practice.date_end:
                practice.date_end_located = format_datetime(
                    self.env, practice.date_end, tz=practice.date_tz, dt_format='medium')
            else:
                practice.date_end_located = False

    @api.depends('date_begin', 'date_end')
    def _compute_is_ongoing(self):
        now = fields.Datetime.now()
        for practice in self:
            practice.is_ongoing = practice.date_begin <= now < practice.date_end

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
        practice_ids = self.env['practice.practice']._search(domain)
        return [('id', 'in', practice_ids)]

    @api.depends('date_begin', 'date_end', 'date_tz')
    def _compute_field_is_one_day(self):
        for practice in self:
            # Need to localize because it could begin late and finish early in
            # another timezone
            practice = practice._set_tz_context()
            begin_tz = fields.Datetime.context_timestamp(practice, practice.date_begin)
            end_tz = fields.Datetime.context_timestamp(practice, practice.date_end)
            practice.is_one_day = (begin_tz.date() == end_tz.date())

    @api.depends('date_end')
    def _compute_is_finished(self):
        for practice in self:
            if not practice.date_end:
                practice.is_finished = False
                continue
            practice = practice._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(practice, fields.Datetime.now())
            datetime_end = fields.Datetime.context_timestamp(practice, practice.date_end)
            practice.is_finished = datetime_end <= current_datetime

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
        practice_ids = self.env['practice.practice']._search(domain)
        return [('id', 'in', practice_ids)]

    @api.depends('practice_type_id')
    def _compute_date_tz(self):
        for practice in self:
            if practice.practice_type_id.default_timezone:
                practice.date_tz = practice.practice_type_id.default_timezone
            if not practice.date_tz:
                practice.date_tz = self.env.user.tz or 'UTC'


    @api.onchange('practice_id')
    def onchange_practice_id(self):
        for rec in self:
            return {'domain': {'practitioner_id': [('practice_id', '=', rec.practice_id.id)]}}

    @api.onchange('practitioner_id')
    def onchange_practitioner_id(self):
        for rec in self:
            return {'domain': {'patient_id': [('practitioner_id', '=', rec.practitioner_id.id)]}}
        
    # @api.onchange('request_date', 'date_end')
    # def _onchange_request_date(self):
    #     """ Warn if the request dates is sooner than the end date """
    #     if (self.request_date and self.date_end and self.request_date < self.date_end):
    #         return {
    #             'warning': {
    #                 'title': _('Requested date is too soon.'),
    #                 'message': _("The request date is sooner than the end date."
    #                              "You may be unable to honor the delivery date.")
    #             }
    #         }


    # seats
    @api.depends('practice_type_id')
    def _compute_seats_max(self):
        """ Update practice configuration from its practice type. Depends are set only
        on practice_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if practice type is changed, update practice configuration. Changing
        practice type content itself should not trigger this method. """
        for practice in self:
            if not practice.practice_type_id:
                practice.seats_max = practice.seats_max or 0
            else:
                practice.seats_max = practice.practice_type_id.seats_max or 0

    @api.depends('practice_type_id')
    def _compute_seats_limited(self):
        """ Update practice configuration from its practice type. Depends are set only
        on practice_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if practice type is changed, update practice configuration. Changing
        practice type content itself should not trigger this method. """
        for practice in self:
            if practice.practice_type_id.has_seats_limitation != practice.seats_limited:
                practice.seats_limited = practice.practice_type_id.has_seats_limitation
            if not practice.seats_limited:
                practice.seats_limited = False

    @api.depends('practice_type_id')
    def _compute_auto_confirm(self):
        """ Update practice configuration from its practice type. Depends are set only
        on practice_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if practice type is changed, update practice configuration. Changing
        practice type content itself should not trigger this method. """
        for practice in self:
            practice.auto_confirm = practice.practice_type_id.auto_confirm

    @api.depends('practice_type_id')
    def _compute_practice_mail_ids(self):
        """ Update practice configuration from its practice type. Depends are set only
        on practice_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if practice type is changed, update practice configuration. Changing
        practice type content itself should not trigger this method.

        When synchronizing mails:

          * lines that are not sent and have no confirmations linked are remove;
          * type lines are added;
        """
        for practice in self:
            if not practice.practice_type_id and not practice.practice_mail_ids:
                practice.practice_mail_ids = self._default_practice_mail_ids()
                continue

            # lines to keep: those with already sent emails or confirmations
            mails_to_remove = practice.practice_mail_ids.filtered(
                lambda mail: not(mail._origin.mail_done) and not(mail._origin.mail_confirmation_ids)
            )
            command = [Command.unlink(mail.id) for mail in mails_to_remove]
            if practice.practice_type_id.practice_type_mail_ids:
                command += [
                    Command.create(line._prepare_practice_mail_values())
                    for line in practice.practice_type_id.practice_type_mail_ids
                ]
            if command:
                practice.practice_mail_ids = command

    @api.depends('practice_type_id')
    def _compute_tag_ids(self):
        """ Update practice configuration from its practice type. Depends are set only
        on practice_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if practice type is changed, update practice configuration. Changing
        practice type content itself should not trigger this method. """
        for practice in self:
            if not practice.tag_ids and practice.practice_type_id.tag_ids:
                practice.tag_ids = practice.practice_type_id.tag_ids

    @api.depends('practice_type_id')
    def _compute_practice_device_ids(self):
        """ Update practice configuration from its practice type. Depends are set only
        on practice_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if practice type is changed, update practice configuration. Changing
        practice type content itself should not trigger this method.

        When synchronizing devices:

          * lines that have no confirmations linked are remove;
          * type lines are added;

        Note that updating practice_device_ids triggers _compute_start_sale_date
        (start_sale_datetime computation) so ensure result to avoid cache miss.
        """
        for practice in self:
            if not practice.practice_type_id and not practice.practice_device_ids:
                practice.practice_device_ids = False
                continue

            # lines to keep: those with existing confirmations
            devices_to_remove = practice.practice_device_ids.filtered(lambda device: not device._origin.confirmation_ids)
            command = [Command.unlink(device.id) for device in devices_to_remove]
            if practice.practice_type_id.practice_type_device_ids:
                command += [
                    Command.create({
                        attribute_name: line[attribute_name] if not isinstance(line[attribute_name], models.BaseModel) else line[attribute_name].id
                        for attribute_name in self.env['practice.type.device']._get_practice_device_fields_whitelist()
                    }) for line in practice.practice_type_id.practice_type_device_ids
                ]
            practice.practice_device_ids = command

    @api.depends('practice_type_id')
    def _compute_note(self):
        for practice in self:
            if practice.practice_type_id and not is_html_empty(practice.practice_type_id.note):
                practice.note = practice.practice_type_id.note

    @api.depends('practice_type_id')
    def _compute_device_instructions(self):
        for practice in self:
            if is_html_empty(practice.device_instructions) and not \
               is_html_empty(practice.practice_type_id.device_instructions):
                practice.device_instructions = practice.practice_type_id.device_instructions

    @api.constrains('seats_max', 'seats_available', 'seats_limited')
    def _check_seats_limit(self):
        if any(practice.seats_limited and practice.seats_max and practice.seats_available < 0 for practice in self):
            raise ValidationError(_('No more available seats.'))

    # @api.constrains('date_begin', 'request_date')
    # def _check_request_date(self):
    #     for practice in self:
    #         if practice.request_date < practice.date_begin:
    #             raise ValidationError(_('The request date cannot be earlier than the beginning date.'))

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['practice.stage'].search([])
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Temporary fix for ``seats_limited`` and ``date_tz`` required fields
            vals.update(self._sync_required_computed(vals))        
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'practice.practice') or _('New')
        practices = super(PracticePractice, self).create(vals_list)
        for res in practices:
            if res.organizer_id:
                res.message_subscribe([res.organizer_id.id])
        practices.flush()
        return practices
    
    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code(
    #             'podiatry.practice') or _('New')
    #     res = super(Practice, self).create(vals)
    #     if res.stage_id.state in ("done", "cancel"):
    #         raise exceptions.UserError(
    #             "State not allowed for new practices."
    #         )
    #     return res

    def write(self, vals):
        if 'stage_id' in vals and 'kanban_state' not in vals:
            # reset kanban state when changing stage
            vals['kanban_state'] = 'normal'
        res = super(PracticePractice, self).write(vals)
        if vals.get('organizer_id'):
            self.message_subscribe([vals['organizer_id']])
        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_("%s (copy)") % (self.name))
        return super(PracticePractice, self).copy(default)

    @api.model
    def _get_mail_message_access(self, res_ids, operation, model_name=None):
        if (
            operation == 'create'
            and self.env.user.has_group('practice.group_practice_confirmation_desk')
            and (not model_name or model_name == 'practice.practice')
        ):
            # allow the confirmation desk users to post messages on Practice
            # can not be done with "_mail_post_access" otherwise public user will be
            # able to post on published Practice (see website_practice)
            return 'read'
        return super(PracticePractice, self)._get_mail_message_access(res_ids, operation, model_name)

    def _sync_required_computed(self, values):
        # TODO: See if the change to seats_limited affects this ?
        """ Call compute fields in cache to find missing values for required fields
        (seats_limited and date_tz) in case they are not given in values """
        missing_fields = list(set(['seats_limited', 'date_tz']).difference(set(values.keys())))
        if missing_fields and values:
            cache_practice = self.new(values)
            cache_practice._compute_seats_limited()
            cache_practice._compute_date_tz()
            return dict((fname, cache_practice[fname]) for fname in missing_fields)
        else:
            return {}

    def _set_tz_context(self):
        self.ensure_one()
        return self.with_context(tz=self.date_tz or 'UTC')

    def action_set_done(self):
        """
        Action which will move the practices
        into the first next (by sequence) stage defined as "Ended"
        (if they are not already in an ended stage)
        """
        first_ended_stage = self.env['practice.stage'].search([('pipe_end', '=', True)], limit=1, order='sequence')
        if first_ended_stage:
            self.write({'stage_id': first_ended_stage.id})

    def mail_attendees(self, template_id, force_send=False, filter_func=lambda self: self.state != 'cancel'):
        for practice in self:
            for attendee in practice.confirmation_ids.filtered(filter_func):
                self.env['mail.template'].browse(template_id).send_mail(attendee.id, force_send=force_send)

    def _get_ics_file(self):
        """ Returns iCalendar file for the practice invitation.
            :returns a dict of .ics file content for each practice
        """
        result = {}
        if not vobject:
            return result

        for practice in self:
            cal = vobject.iCalendar()
            cal_practice = cal.add('vpractice')

            cal_practice.add('created').value = fields.Datetime.now().replace(tzinfo=pytz.timezone('UTC'))
            cal_practice.add('dtstart').value = fields.Datetime.from_string(practice.date_begin).replace(tzinfo=pytz.timezone('UTC'))
            cal_practice.add('dtend').value = fields.Datetime.from_string(practice.date_end).replace(tzinfo=pytz.timezone('UTC'))
            cal_practice.add('summary').value = practice.name
            if practice.address_id:
                cal_practice.add('location').value = practice.sudo().address_id.contact_address

            result[practice.id] = cal.serialize().encode('utf-8')
        return result

    @api.autovacuum
    def _gc_mark_practices_done(self):
        """ move every ended practices in the next 'ended stage' """
        ended_practices = self.env['practice.practice'].search([
            ('date_end', '<', fields.Datetime.now()),
            ('stage_id.pipe_end', '=', False),
        ])
        if ended_practices:
            ended_practices.action_set_done()
