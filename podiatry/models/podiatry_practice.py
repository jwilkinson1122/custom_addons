import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource

import logging

_logger = logging.getLogger(__name__)


class Practice(models.Model):
    _name = 'podiatry.practice'
    _description = "Care Practice"
    _inherit = ['resource.mixin', 'mail.thread',
                'mail.activity.mixin', 'image.mixin']
    _order = 'sequence,id'

    _parent_name = 'parent_id'
    _parent_store = True

    parent_path = fields.Char(string="Parent Path", index=True)

    parent_id = fields.Many2one(
        comodel_name='podiatry.practice',
        string="Parent Practice",
        index=True,
        ondelete='cascade',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    @api.model
    def _get_sequence_code(self):
        return 'podiatry.practice'

    active = fields.Boolean(string="Active", default=True, tracking=True)
    name = fields.Char(string="Practice Name", index=True, translate=True)
    color = fields.Integer(string="Color Index (0-15)")

    sequence = fields.Integer(
        string="Sequence", required=True,
        default=5,
    )

    code = fields.Char(string="Code", copy=False)

    full_name = fields.Char(
        string="Full Name",
        compute='_compute_full_name',
        store=True,
    )

    identification = fields.Char(string="Identification", index=True)
    reference = fields.Char(string='Practice Reference', required=True, copy=False, readonly=True,
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

    @api.depends('name', 'parent_id.full_name')
    def _compute_full_name(self):
        for practice in self:
            if practice.parent_id:
                practice.full_name = "%s / %s" % (
                    practice.parent_id.full_name, practice.name)
            else:
                practice.full_name = practice.name
        return

    notes = fields.Text(string="Notes")

    patient_id = fields.One2many(
        comodel_name='podiatry.patient',
        inverse_name='practice_id',
        string="Patients",
    )

    practitioner_id = fields.One2many(
        comodel_name='podiatry.practitioner',
        inverse_name='practice_id',
        string="Contacts",
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Created by",
    )

    practice_prescription_id = fields.One2many(
        comodel_name='podiatry.prescription',
        inverse_name='practice_id',
        string="Prescriptions",
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner', string="Contact",
    )

    speciality_id = fields.Many2one(
        comodel_name='podiatry.speciality',
        string='speciality')

    other_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='podiatry_practice_partners_rel',
        column1='practice_id', column2='partner_id',
        string="Other Contacts",
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )

    child_ids = fields.One2many(
        comodel_name='podiatry.practice',
        inverse_name='parent_id',
        string="Practices",
    )
    child_count = fields.Integer(
        string="Subpractice Count",
        compute='_compute_child_count',
    )

    @api.depends('child_ids')
    def _compute_child_count(self):
        for practice in self:
            practice.child_count = len(practice.child_ids)
        return

    same_reference_practice_id = fields.Many2one(
        comodel_name='podiatry.practice',
        string='Practice with same Identity',
        compute='_compute_same_reference_practice_id',
    )

    @api.depends('reference')
    def _compute_same_reference_practice_id(self):
        for practice in self:
            domain = [
                ('reference', '=', practice.reference),
            ]

            origin_id = practice._origin.id

            if origin_id:
                domain += [('id', '!=', origin_id)]

            practice.same_reference_practice_id = bool(practice.reference) and \
                self.with_context(active_test=False).sudo().search(
                    domain, limit=1)

    # @api.model_create_multi
    # def create(self, values):
    #     return super(Practice, self.with_context(default_resource_type='material')).create(values)

    # def name_get(self):
    #     if not self.env.context.get('hierarchical_naming', True):
    #         return [(record.id, record.name) for record in self]
    #     return super(Practice, self).name_get()

    # @api.model
    # def _set_code(self):
    #     for practice in self:
    #         sequence = self._get_sequence_code()
    #         practice.code = self.env['ir.sequence'].next_by_code(sequence)
    #     return

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'podiatry', 'static/src/img', 'company_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _set_code(self):
        for practice in self:
            sequence = self._get_sequence_code()
            practice.code = self.env['ir.sequence'].next_by_code(
                sequence)
        return

    @api.model
    def create(self, vals):
        if not vals.get('notes'):
            vals['notes'] = 'New Practice'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'podiatry.practice') or _('New')
        practice = super(Practice, self).create(vals)
        practice._set_code()
        return practice

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.reference + '] ' + rec.name
            result.append((rec.id, name))
        return result

    def write(self, values):
        result = super(Practice, self).write(values)
        return result

    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'podiatry.prescription',
            'domain': [('practice_id', '=', self.id)],
            'context': {'default_practice_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
