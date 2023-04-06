# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PrescriptionTemplateDevice(models.Model):
    _name = 'prescription.type.device'
    _description = 'Prescription Template Device'

    # description
    name = fields.Char(
        string='Name', default=lambda self: _('Confirmation'),
        required=True, translate=True)
    description = fields.Text(
        'Description', translate=True,
        help="A description of the device that you want to communicate to your customers.")
    prescription_type_id = fields.Many2one(
        'prescription.type', string='Prescription Category', ondelete='cascade', required=True)
    # seats
    seats_limited = fields.Boolean(string='Seats Limit', readonly=True, store=True,
                                   compute='_compute_seats_limited')
    seats_max = fields.Integer(
        string='Maximum Seats',
        help="Define the number of available devices. If you have too many confirmations you will "
             "not be able to sell devices anymore. Set 0 to ignore this rule set as unlimited.")

    @api.depends('seats_max')
    def _compute_seats_limited(self):
        for device in self:
            device.seats_limited = device.seats_max

    @api.model
    def _get_prescription_device_fields_whitelist(self):
        """ Whitelist of fields that are copied from prescription_type_device_ids to prescription_device_ids when
        changing the prescription_type_id field of prescription.prescription """
        return ['name', 'description', 'seats_max']


class PrescriptionDevice(models.Model):
    """ Device model allowing to have differnt kind of confirmations for a given
    prescription. Device are based on device type as they share some common fields
    and behavior. Those models come from <= v13 Odoo prescription.prescription.device that
    modeled both concept: devices for prescription templates, and devices for prescriptions. """
    _name = 'prescription.prescription.device'
    _inherit = 'prescription.type.device'
    _description = 'Prescription Device'

    @api.model
    def default_get(self, fields):
        res = super(PrescriptionDevice, self).default_get(fields)
        if 'name' in fields and (not res.get('name') or res['name'] == _('Confirmation')) and self.env.context.get('default_prescription_name'):
            res['name'] = _('Confirmation for %s', self.env.context['default_prescription_name'])
        return res

    # description
    prescription_type_id = fields.Many2one(ondelete='set null', required=False)
    prescription_id = fields.Many2one(
        'prescription.prescription', string="Prescription",
        ondelete='cascade', required=True)
    company_id = fields.Many2one('res.company', related='prescription_id.company_id')
    # sale
    start_sale_datetime = fields.Datetime(string="Confirmation Start")
    end_sale_datetime = fields.Datetime(string="Confirmation Complete")
    is_expired = fields.Boolean(string='Is Expired', compute='_compute_is_expired')
    sale_available = fields.Boolean(string='Is Available', compute='_compute_sale_available', compute_sudo=True)
    confirmation_ids = fields.One2many('prescription.confirmation', 'prescription_device_id', string='Confirmations')
    # seats
    seats_reserved = fields.Integer(string='Reserved Seats', compute='_compute_seats', store=True)
    seats_available = fields.Integer(string='Available Seats', compute='_compute_seats', store=True)
    seats_unconfirmed = fields.Integer(string='Unconfirmed Seats', compute='_compute_seats', store=True)
    seats_used = fields.Integer(string='Used Seats', compute='_compute_seats', store=True)

    @api.depends('end_sale_datetime', 'prescription_id.date_tz')
    def _compute_is_expired(self):
        for device in self:
            device = device._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(device, fields.Datetime.now())
            if device.end_sale_datetime:
                end_sale_datetime = fields.Datetime.context_timestamp(device, device.end_sale_datetime)
                device.is_expired = end_sale_datetime < current_datetime
            else:
                device.is_expired = False

    @api.depends('is_expired', 'start_sale_datetime', 'prescription_id.date_tz', 'seats_available', 'seats_max')
    def _compute_sale_available(self):
        for device in self:
            if not device.is_launched() or device.is_expired or (device.seats_max and device.seats_available <= 0):
                device.sale_available = False
            else:
                device.sale_available = True

    @api.depends('seats_max', 'confirmation_ids.state')
    def _compute_seats(self):
        """ Determine reserved, available, reserved but unconfirmed and used seats. """
        # initialize fields to 0 + compute seats availability
        for device in self:
            device.seats_unconfirmed = device.seats_reserved = device.seats_used = device.seats_available = 0
        # aggregate confirmations by device and by state
        results = {}
        if self.ids:
            state_field = {
                'draft': 'seats_unconfirmed',
                'open': 'seats_reserved',
                'done': 'seats_used',
            }
            query = """ SELECT prescription_device_id, state, count(prescription_id)
                        FROM prescription_confirmation
                        WHERE prescription_device_id IN %s AND state IN ('draft', 'open', 'done')
                        GROUP BY prescription_device_id, state
                    """
            self.env['prescription.confirmation'].flush(['prescription_id', 'prescription_device_id', 'state'])
            self.env.cr.execute(query, (tuple(self.ids),))
            for prescription_device_id, state, num in self.env.cr.fetchall():
                results.setdefault(prescription_device_id, {})[state_field[state]] = num

        # compute seats_available
        for device in self:
            device.update(results.get(device._origin.id or device.id, {}))
            if device.seats_max > 0:
                device.seats_available = device.seats_max - (device.seats_reserved + device.seats_used)

    @api.constrains('start_sale_datetime', 'end_sale_datetime')
    def _constrains_dates_coherency(self):
        for device in self:
            if device.start_sale_datetime and device.end_sale_datetime and device.start_sale_datetime > device.end_sale_datetime:
                raise UserError(_('The stop date cannot be earlier than the start date.'))

    @api.constrains('seats_available', 'seats_max')
    def _constrains_seats_available(self):
        if any(record.seats_max and record.seats_available < 0 for record in self):
            raise ValidationError(_('No more available seats for this device.'))

    def _get_device_multiline_description(self):
        """ Compute a multiline description of this device. It is used when device
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
            device = self._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(device, fields.Datetime.now())
            start_sale_datetime = fields.Datetime.context_timestamp(device, device.start_sale_datetime)
            return start_sale_datetime <= current_datetime
        else:
            return True

    @api.ondelete(at_uninstall=False)
    def _unlink_except_if_confirmations(self):
        if self.confirmation_ids:
            raise UserError(_(
                "The following devices cannot be deleted while they have one or more confirmations linked to them:\n- %s",
                '\n- '.join(self.mapped('name'))))
