# -*- coding: utf-8 -*-

import base64
from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

import logging

_logger = logging.getLogger(__name__)


class Practice(models.Model):
    _name = 'pod.practice'
    _description = 'pod.practice'
    _inherits = {
        'res.partner': 'partner_id',
    }

    _rec_name = 'practice_id'

    _parent_name = 'parent_id'
    _parent_store = True

    parent_path = fields.Char(string="Parent Path", index=True)

    parent_id = fields.Many2one(
        comodel_name='pod.practice',
        string="Parent Practice",
        index=True,
        ondelete='cascade',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )

    child_ids = fields.One2many(
        comodel_name='pod.practice',
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

    sequence = fields.Integer(
        string="Sequence", required=True,
        default=5,
    )

    code = fields.Char(string="Code", copy=False)
    active = fields.Boolean(string="Active", default=True, tracking=True)

    @api.onchange('practice_id')
    def _onchange_practice(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.practice_id
        self.practice_address_id = address_id

    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='restrict',
                                 help='Partner-related data of the Practice')

    notes = fields.Text(string="Notes")
    practice_id = fields.Many2many('res.partner', domain=[(
        'is_practice', '=', True)], string="practice", required=True)
    email = fields.Char(string="E-mail")
    phone = fields.Char(string="Telephone")
    mobile = fields.Char(string="Mobile")
    practice_address_id = fields.Many2one('res.partner', string="Address", )
    street = fields.Char(related='practice_id.street', readonly=False)
    street2 = fields.Char(related='practice_id.street2', readonly=False)
    zip_code = fields.Char(related='practice_id.zip', readonly=False)
    city = fields.Char(related='practice_id.city', readonly=False)
    zip = fields.Char(string="ZIP Code")
    state_id = fields.Many2one(
        "res.country.state", related='practice_id.state_id', readonly=False)
    country_id = fields.Many2one(
        'res.country', related='practice_id.country_id', readonly=False)
    doctor_ids = fields.Many2many('pod.doctor', string="Doctors")
    # patient_ids = fields.One2many('pod.patient', string="Patients")
    # prescription_ids = fields.One2many(
    #     'doctor.prescription', string="Prescriptions")
    patient_ids = fields.One2many(
        comodel_name='pod.patient',
        inverse_name='practice_id',
        string="Patients",
    )
    prescription_ids = fields.One2many(
        comodel_name='doctor.prescription',
        inverse_name='practice_id',
        string="Prescriptions",
    )
    identification = fields.Char(string="Identification", index=True)
    reference = fields.Char(string='Practice Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))

    @api.model
    def _get_sequence_code(self):
        return 'pod.practice'

    full_name = fields.Char(
        string="Full Name",
        compute='_compute_full_name',
        store=True,
    )

    @api.depends('name', 'parent_id.full_name')
    def _compute_full_name(self):
        for practice in self:
            if practice.parent_id:
                practice.full_name = "%s / %s" % (
                    practice.parent_id.full_name, practice.name)
            else:
                practice.full_name = practice.name
        return

    same_reference_practice_id = fields.Many2one(
        comodel_name='pod.practice',
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

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'pod_erp', 'static/src/description', 'company_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _set_code(self):
        for practice in self:
            sequence = self._get_sequence_code()
            practice.code = self.env['ir.sequence'].next_by_code(
                sequence)
        return

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code(
    #             'pod.prescription.sequence')
    #     result = super(DoctorPrescription, self).create(vals)
    #     return result

    @api.model
    def create(self, vals):
        if not vals.get('notes'):
            vals['notes'] = 'New Practice'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'pod.practice') or _('New')
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
    # def create(self,val):
    #     practice_id  = self.env['ir.sequence'].next_by_code('pod.practice')
    #     if practice_id:
    #         val.update({
    #                     'name':practice_id,
    #                    })
    #     result = super(Practice, self).create(val)
    #     return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate practice.'))

    # def action_open_prescriptions(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Prescriptions',
    #         'res_model': 'pod.prescription',
    #         'domain': [('practice_id', '=', self.id)],
    #         'context': {'default_practice_id': self.id},
    #         'view_mode': 'kanban,tree,form',
    #         'target': 'current',
    #     }


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: