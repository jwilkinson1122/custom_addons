# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PrescriptionTemplateTicket(models.Model):
    _name = 'prescription.type.ticket'
    _description = 'Prescription Template Ticket'

    # description
    name = fields.Char(
        string='Name', default=lambda self: _('Registration'),
        required=True, translate=True)
    description = fields.Text(
        'Description', translate=True,
        help="A description of the ticket that you want to communicate to your customers.")
    prescription_type_id = fields.Many2one(
        'prescription.type', string='Prescription Category', ondelete='cascade', required=True)
    # seats
    seats_limited = fields.Boolean(string='Seats Limit', readonly=True, store=True,
                                   compute='_compute_seats_limited')
    seats_max = fields.Integer(
        string='Maximum Seats',
        help="Define the number of available tickets. If you have too many registrations you will "
             "not be able to sell tickets anymore. Set 0 to ignore this rule set as unlimited.")

    @api.depends('seats_max')
    def _compute_seats_limited(self):
        for ticket in self:
            ticket.seats_limited = ticket.seats_max

    @api.model
    def _get_prescription_ticket_fields_whitelist(self):
        """ Whitelist of fields that are copied from prescription_type_ticket_ids to prescription_ticket_ids when
        changing the prescription_type_id field of prescription.prescription """
        return ['name', 'description', 'seats_max']


class PrescriptionTicket(models.Model):
    """ Ticket model allowing to have differnt kind of registrations for a given
    prescription. Ticket are based on ticket type as they share some common fields
    and behavior. Those models come from <= v13 Odoo prescription.prescription.ticket that
    modeled both concept: tickets for prescription templates, and tickets for prescriptions. """
    _name = 'prescription.prescription.ticket'
    _inherit = 'prescription.type.ticket'
    _description = 'Prescription Ticket'

    @api.model
    def default_get(self, fields):
        res = super(PrescriptionTicket, self).default_get(fields)
        if 'name' in fields and (not res.get('name') or res['name'] == _('Registration')) and self.env.context.get('default_prescription_name'):
            res['name'] = _('Registration for %s', self.env.context['default_prescription_name'])
        return res

    # description
    prescription_type_id = fields.Many2one(ondelete='set null', required=False)
    prescription_id = fields.Many2one(
        'prescription.prescription', string="Prescription",
        ondelete='cascade', required=True)
    company_id = fields.Many2one('res.company', related='prescription_id.company_id')
    # sale
    start_sale_datetime = fields.Datetime(string="Registration Start")
    end_sale_datetime = fields.Datetime(string="Registration End")
    is_expired = fields.Boolean(string='Is Expired', compute='_compute_is_expired')
    sale_available = fields.Boolean(string='Is Available', compute='_compute_sale_available', compute_sudo=True)
    registration_ids = fields.One2many('prescription.registration', 'prescription_ticket_id', string='Registrations')
    # seats
    seats_reserved = fields.Integer(string='Reserved Seats', compute='_compute_seats', store=True)
    seats_available = fields.Integer(string='Available Seats', compute='_compute_seats', store=True)
    seats_unconfirmed = fields.Integer(string='Unconfirmed Seats', compute='_compute_seats', store=True)
    seats_used = fields.Integer(string='Used Seats', compute='_compute_seats', store=True)

    @api.depends('end_sale_datetime', 'prescription_id.date_tz')
    def _compute_is_expired(self):
        for ticket in self:
            ticket = ticket._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(ticket, fields.Datetime.now())
            if ticket.end_sale_datetime:
                end_sale_datetime = fields.Datetime.context_timestamp(ticket, ticket.end_sale_datetime)
                ticket.is_expired = end_sale_datetime < current_datetime
            else:
                ticket.is_expired = False

    @api.depends('is_expired', 'start_sale_datetime', 'prescription_id.date_tz', 'seats_available', 'seats_max')
    def _compute_sale_available(self):
        for ticket in self:
            if not ticket.is_launched() or ticket.is_expired or (ticket.seats_max and ticket.seats_available <= 0):
                ticket.sale_available = False
            else:
                ticket.sale_available = True

    @api.depends('seats_max', 'registration_ids.state')
    def _compute_seats(self):
        """ Determine reserved, available, reserved but unconfirmed and used seats. """
        # initialize fields to 0 + compute seats availability
        for ticket in self:
            ticket.seats_unconfirmed = ticket.seats_reserved = ticket.seats_used = ticket.seats_available = 0
        # aggregate registrations by ticket and by state
        results = {}
        if self.ids:
            state_field = {
                'draft': 'seats_unconfirmed',
                'open': 'seats_reserved',
                'done': 'seats_used',
            }
            query = """ SELECT prescription_ticket_id, state, count(prescription_id)
                        FROM prescription_registration
                        WHERE prescription_ticket_id IN %s AND state IN ('draft', 'open', 'done')
                        GROUP BY prescription_ticket_id, state
                    """
            self.env['prescription.registration'].flush(['prescription_id', 'prescription_ticket_id', 'state'])
            self.env.cr.execute(query, (tuple(self.ids),))
            for prescription_ticket_id, state, num in self.env.cr.fetchall():
                results.setdefault(prescription_ticket_id, {})[state_field[state]] = num

        # compute seats_available
        for ticket in self:
            ticket.update(results.get(ticket._origin.id or ticket.id, {}))
            if ticket.seats_max > 0:
                ticket.seats_available = ticket.seats_max - (ticket.seats_reserved + ticket.seats_used)

    @api.constrains('start_sale_datetime', 'end_sale_datetime')
    def _constrains_dates_coherency(self):
        for ticket in self:
            if ticket.start_sale_datetime and ticket.end_sale_datetime and ticket.start_sale_datetime > ticket.end_sale_datetime:
                raise UserError(_('The stop date cannot be earlier than the start date.'))

    @api.constrains('seats_available', 'seats_max')
    def _constrains_seats_available(self):
        if any(record.seats_max and record.seats_available < 0 for record in self):
            raise ValidationError(_('No more available seats for this ticket.'))

    def _get_ticket_multiline_description(self):
        """ Compute a multiline description of this ticket. It is used when ticket
        description are necessary without having to encode it manually, like sales
        information. """
        return '%s\n%s' % (self.display_name, self.prescription_id.display_name)

    def _set_tz_context(self):
        self.ensure_one()
        return self.with_context(tz=self.prescription_id.date_tz or 'UTC')

    def is_launched(self):
        # TDE FIXME: in master, make a computed field, easier to use
        self.ensure_one()
        if self.start_sale_datetime:
            ticket = self._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(ticket, fields.Datetime.now())
            start_sale_datetime = fields.Datetime.context_timestamp(ticket, ticket.start_sale_datetime)
            return start_sale_datetime <= current_datetime
        else:
            return True

    @api.ondelete(at_uninstall=False)
    def _unlink_except_if_registrations(self):
        if self.registration_ids:
            raise UserError(_(
                "The following tickets cannot be deleted while they have one or more registrations linked to them:\n- %s",
                '\n- '.join(self.mapped('name'))))
