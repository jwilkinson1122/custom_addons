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
    _description = 'Medical Practitioner'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'practitioner_id'

    _sql_constraints = [(
        'podiatry_practitioner_unique_code',
        'UNIQUE (code)',
        'Internal ID must be unique',
    )]
    

    patient_ids = fields.One2many(
        comodel_name='podiatry.patient',
        inverse_name='practitioner_id',
        string='Patients'
    )
    
    patient_count = fields.Integer(
        string='Patient Count', compute='_compute_patient_count')

    def _compute_patient_count(self):
        for rec in self:
            patient_count = self.env['podiatry.patient'].search_count(
                [('practitioner_id', '=', rec.id)])
            rec.patient_count = patient_count

    is_practitioner = fields.Boolean()
    
    # Personal Information
    practitioner_id = fields.Many2many('res.partner', domain=[('is_practitioner', '=', True)], string="practitioner_id", required=True)
    reference_no = fields.Char(string='Reference No.')
    practitioner_relation_label = fields.Char('Practitioner relation label', translate=True, default='Attached To:', readonly=True)

    role_ids = fields.Many2many(string='Type',comodel_name='podiatry.role')
    
    specialty_ids = fields.Many2many(string='Specialties', comodel_name='podiatry.specialty')
    
    practitioner_type = fields.Selection(
        string='Entity Type',
        selection=[('internal', 'Internal Entity'),
                   ('external', 'External Entity')],
        readonly=False,
    )
    
    # practice_email = fields.Char(related='parent_id.email', string="Email")

    practice_id = fields.Many2one(comodel_name='podiatry.practice', string='Practice')

    other_practice_ids = fields.Many2many(string='Other', comodel_name='podiatry.practice')

    # practitioner_prescription_id = fields.One2many(
    #     comodel_name='podiatry.prescription',
    #     inverse_name='practitioner_id',
    #     string='Prescriptions')
    practitioner_prescription_id = fields.One2many(
        "podiatry.prescription",
        "practitioner_id",
        string="Practitioner Prescriptions",
        domain=[("active", "=", True)],
    )

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
    reference = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))

    # Related Practice Information
    # practice_type = fields.Selection(related='parent_id.type', string="Type", readonly=True, default=lambda self: _('Address Type'))
    practice_type = fields.Selection(related='practice_id.type', string="Type", readonly=True, default=lambda self: _('Address Type'))

    practice_email = fields.Char(related='practice_id.email', string="Email")
    practice_phone = fields.Char(related='practice_id.phone', string="Telephone")
    practice_mobile = fields.Char(related='practice_id.mobile', string="Mobile")
    practice_street = fields.Char(related='practice_id.street', string="Street")
    practice_street2 = fields.Char(related='practice_id.street2', string="Street")
    practice_country_id = fields.Many2one('res.country', related='practice_id.country_id', string="Country")
    practice_state_id = fields.Many2one('res.country.state', related='practice_id.state_id', string="State")
    practice_city= fields.Char(related='practice_id.city', string="City")
    practice_zip = fields.Char(related='practice_id.zip', string="Zip")
    

    

    notes = fields.Text(string="Notes")

    salutation = fields.Selection(selection=[
        ('practitioner', 'Practitioner'),
        ('mr', 'Mr.'),
        ('ms', 'Ms.'),
        ('mrs', 'Mrs.'),
    ], string="Salutation")

    signature = fields.Binary(string="Signature")

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')

    prescription_device_lines = fields.One2many(
        'prescription.device.line', 'prescription_id', 'Prescription Line')

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['podiatry.prescription'].search_count(
                [('practitioner_id', '=', rec.id)])
            rec.prescription_count = prescription_count

    prescription_date = fields.Datetime(
        'Prescription Date', default=fields.Datetime.now)

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
    
    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

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
        
        
    def action_open_patients(self):
            return {
            'type': 'ir.actions.act_window',
            'name': 'Patients',
            'res_model': 'podiatry.patient',
            'domain': [('practitioner_id', '=', self.id)],
            'context': {'default_practitioner_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }

    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'podiatry.prescription',
            'domain': [('practitioner_id', '=', self.id)],
            'context': {
                'default_practitioner_id': self.id,
                # 'default_reference_no': self.reference_no,
                },
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
        
    def open_parent(self):
        """Utility method used to add an "Open Parent" button in partner
        views"""
        self.ensure_one()
        address_form_id = self.env.ref("base.view_partner_address_form").id
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "form",
            "views": [(address_form_id, "form")],
            "res_id": self.parent_id.id,
            "target": "new",
            "flags": {"form": {"action_buttons": True}},
        }
        
        
        # def name_get(self):
        #     result = []
        # for rec in self:
        #     name = '[' + rec.reference + '] ' + rec.name
        #     result.append((rec.id, name))
        # return result
    
    def action_add_communication(self):
        for rec in self:
            rec.reference_no = rec.reference
            # rec.reference_no = rec.env['ir.sequence'].next_by_code('res.partner.patient')
            self.ensure_one()
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = \
                    ir_model_data._xmlid_to_res_id('podiatry.email_template_send_reference_no')
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data._xmlid_to_res_id('mail.email_compose_message_wizard_form')
            except ValueError:
                compose_form_id = False
            ctx = {
                'default_model': 'res.partner',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'proforma': self.env.context.get('proforma', False),
                'force_email': True
            }
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }

    def send_birthday_wish(self):
        for rec in self:
            print('hiiiiii--------------------------')
            user_id = rec.create_uid
            template = self.env.ref('podiatry.email_template_send_birthday')
            ctx = self._context.copy()
            template.with_context(ctx).send_mail(user_id.id, force_send=True)

            # self.ensure_one()
            # ir_model_data = self.env['ir.model.data']
            # try:
            #     template_id = \
            #         ir_model_data.get_object_reference('hospital_management_app',
            #                                            'email_template_send_birthday')[1]
            # except ValueError:
            #     template_id = False
            # try:
            #     compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            # except ValueError:
            #     compose_form_id = False
            # ctx = {
            #     'default_model': 'res.partner',
            #     'default_res_id': self.ids[0],
            #     'default_use_template': bool(template_id),
            #     'default_template_id': template_id,
            #     'default_composition_mode': 'comment',
            #     'mark_so_as_sent': True,
            #     'proforma': self.env.context.get('proforma', False),
            #     'force_email': True
            # }
            # return {
            #     'type': 'ir.actions.act_window',
            #     'view_type': 'form',
            #     'view_mode': 'form',
            #     'res_model': 'mail.compose.message',
            #     'views': [(compose_form_id, 'form')],
            #     'view_id': compose_form_id,
            #     'target': 'new',
            #     'context': ctx,
            # }
  


