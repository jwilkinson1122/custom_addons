import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

from . import podiatry_practice

# from lxml import etree
# added import statement in try-except because when server runs on
# windows operating system issue arise because this library is not in Windows.
try:
    from odoo.tools import image_colorize
except:
    image_colorize = False


class Practitioner(models.Model):
    _name = 'podiatry.practitioner'
    _inherit = ['mail.thread',
                'mail.activity.mixin', 'image.mixin']

    _inherits = {
        'res.partner': 'partner_id',
    }

    _rec_name = 'practitioner_id'

    _description = 'practitioner'

    patient_ids = fields.One2many(
        comodel_name='podiatry.patient',
        inverse_name='practitioner_id',
        string='Patients'
    )

    is_practitioner = fields.Boolean()

    practitioner_id = fields.Many2many('res.partner', domain=[(
        'is_practitioner', '=', True)], string="practitioner_id", required=True)

    practice_id = fields.Many2one(
        comodel_name='podiatry.practice',
        string='Practice')

    practitioner_folio_id = fields.One2many(
        comodel_name='podiatry.folio',
        inverse_name='practitioner_id',
        string='Folios')

    @api.model
    def _default_image(self):
        '''Method to get default Image'''
        image_path = get_module_resource('hr', 'static/src/img',
                                         'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    active = fields.Boolean(string="Active", default=True, tracking=True)
    # name = fields.Char(string="Name", index=True)
    color = fields.Integer(string="Color Index (0-15)")
    code = fields.Char(string="Code", copy=False)
    reference = fields.Char(string='Practitioner Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    email = fields.Char(string="E-mail")
    phone = fields.Char(string="Telephone")
    mobile = fields.Char(string="Mobile")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")

    country_id = fields.Many2one(
        comodel_name='res.country', string="Country",
        default=lambda self: self.env.company.country_id,
    )

    state_id = fields.Many2one(
        comodel_name='res.country.state', string="State",
        default=lambda self: self.env.company.state_id,
    )

    city = fields.Char(string="City")
    zip = fields.Char(string="ZIP Code")

    notes = fields.Text(string="Notes")

    salutation = fields.Selection(selection=[
        ('practitioner', 'Practitioner'),
        ('mr', 'Mr.'),
        ('ms', 'Ms.'),
        ('mrs', 'Mrs.'),
    ], string="Salutation")
    
    practitioner_type = fields.Selection([('doctor', 'Doctor'),
                                      ('assistant', 'Assistant'),
                                      ('nurse', 'Nurse'),
                                      ('other', 'Other')],
                                     string="Practice Type")


    signature = fields.Binary(string="Signature")

    folio_count = fields.Integer(
        string='Folio Count', compute='_compute_folio_count')

    practitioner_folio_id = fields.One2many(
        comodel_name='podiatry.folio',
        inverse_name='practitioner_id',
        string="Folios",
    )

    folio_line = fields.One2many(
        'podiatry.folio.line', 'name', 'Folio Line')

    def _compute_folio_count(self):
        for rec in self:
            folio_count = self.env['podiatry.folio'].search_count(
                [('practitioner_id', '=', rec.id)])
            rec.folio_count = folio_count

    folio_date = fields.Datetime(
        'Folio Date', default=fields.Datetime.now)

    user_id = fields.Many2one(
        comodel_name='res.users', string="User",
    )

    responsible_id = fields.Many2one(
        comodel_name='res.users', string="Created By",
        default=lambda self: self.env.user,
    )

    @api.onchange('practitioner_id')
    def _onchange_practitioner(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.practitioner_id
        self.practitioner_address_id = address_id

    practitioner_address_id = fields.Many2one(
        'res.partner', string="Practitioner Address", )

    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='cascade',
                                 help='Partner-related data of the Practitioner')

    def unlink(self):
        self.partner_id.unlink()
        return super(Practitioner, self).unlink()

    other_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='podiatry_practitioner_partners_rel',
        column1='practitioner_id', column2='partner_id',
        string="Other Contacts",
    )

    @api.model
    def _relativedelta_to_text(self, delta):
        result = []

        if delta:
            if delta.years > 0:
                result.append(
                    "{years} {practitioner}".format(
                        years=delta.years,
                        practitioner=_(
                            "year") if delta.years == 1 else _("years"),
                    )
                )
            if delta.months > 0 and delta.years < 9:
                result.append(
                    "{months} {practitioner}".format(
                        months=delta.months,
                        practitioner=_("month") if delta.months == 1 else _(
                            "months"),
                    )
                )
            if delta.days > 0 and not delta.years:
                result.append(
                    "{days} {practitioner}".format(
                        days=delta.days,
                        practitioner=_(
                            "day") if delta.days == 1 else _("days"),
                    )
                )

        return bool(result) and " ".join(result)

    same_reference_practitioner_id = fields.Many2one(
        comodel_name='podiatry.practitioner',
        string='Practitioner with same Identity',
        compute='_compute_same_reference_practitioner_id',
    )

    @api.depends('reference')
    def _compute_same_reference_practitioner_id(self):
        for practitioner in self:
            domain = [
                ('reference', '=', practitioner.reference),
            ]

            origin_id = practitioner._origin.id

            if origin_id:
                domain += [('id', '!=', origin_id)]

            practitioner.same_reference_practitioner_id = bool(practitioner.reference) and \
                self.with_context(active_test=False).sudo().search(
                    domain, limit=1)

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'podiatry', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _add_followers(self):
        for practitioner in self:
            partner_ids = (practitioner.user_id.partner_id |
                           practitioner.responsible_id.partner_id).ids
            practitioner.message_subscribe(partner_ids=partner_ids)

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.model
    def create(self, vals):
        if not vals.get('notes'):
            vals['notes'] = 'New Practitioner'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'podiatry.practitioner') or _('New')
        practitioner = super(Practitioner, self).create(vals)
        practitioner._add_followers()
        return practitioner

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.reference + '] ' + rec.name
            result.append((rec.id, name))
        return result

    def write(self, values):
        result = super(Practitioner, self).write(values)
        if 'user_id' in values or 'other_partner_ids' in values:
            self._add_followers()
        return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate practitioner.'))

    def action_open_folios(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Folios',
            'res_model': 'podiatry.folio',
            'domain': [('practitioner_id', '=', self.id)],
            'context': {'default_practitioner_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
