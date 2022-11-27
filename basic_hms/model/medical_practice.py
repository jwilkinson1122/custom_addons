# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import base64
from odoo import api, fields, models, _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

import logging

_logger = logging.getLogger(__name__)

class medical_practice(models.Model):
    
    _name = 'medical.practice'
    _description = 'medical practice'
    _rec_name = 'practice_id'
    
    _parent_name = 'parent_id'
    _parent_store = True

    parent_path = fields.Char(string="Parent Path", index=True)

    parent_id = fields.Many2one(
        comodel_name='medical.practice',
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
        comodel_name='medical.practice',
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

    partner_id = fields.Many2one('res.partner','Medical Practice', required=True)

    # partner_id = fields.Many2one('res.partner','Physician',required=True)
    # practice_partner_id = fields.Many2one('res.partner',domain=[('is_practice','=',True)],string='Practice')
    # code = fields.Char('Id')
    # info = fields.Text('Extra Info')
    notes = fields.Text(string="Notes")
    practice_id = fields.Many2many('res.partner',domain=[('is_practice','=',True)],string="practice", required= True)
    practice_name = fields.Char(string="Practice Name", index=True, translate=True)
    name = fields.Char(string='ID', readonly=True)
    practice_address_id = fields.Many2one('res.partner', string="Address", )
    street = fields.Char(related='practice_id.street', readonly=False)
    street2 = fields.Char(related='practice_id.street2', readonly=False)
    zip_code = fields.Char(related='practice_id.zip', readonly=False)
    city = fields.Char(related='practice_id.city', readonly=False)
    state_id = fields.Many2one("res.country.state", related='practice_id.state_id', readonly=False)
    country_id = fields.Many2one('res.country', related='practice_id.country_id', readonly=False)
    practitioner_ids = fields.Many2many('medical.physician', string="Doctors")
    patient_ids = fields.Many2many('medical.patient', string="Patients")
    identification = fields.Char(string="Identification", index=True)
    reference = fields.Char(string='Practice Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    
    @api.model
    def _get_sequence_code(self):
        return 'medical.practice'
    
    full_name = fields.Char(
        string="Full Name",
        compute='_compute_full_name',
        store=True,
    )

    @api.depends('practice_name', 'parent_id.full_name')
    def _compute_full_name(self):
        for practice in self:
            if practice.parent_id:
                practice.full_name = "%s / %s" % (
                    practice.parent_id.full_name, practice.practice_name)
            else:
                practice.full_name = practice.practice_name
        return
    
    same_reference_practice_id = fields.Many2one(
        comodel_name='medical.practice',
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
            'basic_hms', 'static/src/img', 'company_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _set_code(self):
        for practice in self:
            sequence = self._get_sequence_code()
            practice.code = self.env['ir.sequence'].next_by_code(
                sequence)
        return

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.model
    def create(self, vals):
        if not vals.get('notes'):
            vals['notes'] = 'New Practice'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'medical.practice') or _('New')
        practice = super(medical_practice, self).create(vals)
        practice._set_code()
        return practice

    def name_get(self):
        result = []
        for rec in self:
            practice_name = '[' + rec.reference + '] ' + rec.practice_name
            result.append((rec.id, practice_name))
        return result

    def write(self, values):
        result = super(medical_practice, self).write(values)
        return result
    # def create(self,val):
    #     practice_id  = self.env['ir.sequence'].next_by_code('medical.practice')
    #     if practice_id:
    #         val.update({
    #                     'name':practice_id,
    #                    })
    #     result = super(medical_practice, self).create(val)
    #     return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate practice.' ))
        
        
    # def action_open_prescriptions(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Prescriptions',
    #         'res_model': 'medical.prescription',
    #         'domain': [('practice_id', '=', self.id)],
    #         'context': {'default_practice_id': self.id},
    #         'view_mode': 'kanban,tree,form',
    #         'target': 'current',
    #     }

        
        

# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
