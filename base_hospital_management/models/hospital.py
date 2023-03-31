# -*- coding: utf-8 -*-

import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

class Hospital(models.Model):
    _inherit = 'res.partner'
    # _name = 'hospital.hospital'
    _description = 'Hospital'
    _parent_name = 'parent_id'
    _parent_store = True
    _order = 'sequence,id'
    # _rec_name = 'name'
    
    sequence = fields.Integer(
        string="Sequence", required=True,
        default=5,
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )
    
    # parent_id = fields.Many2one('res.company', string='Parent Company', index=True)
    # child_ids = fields.One2many('res.company', 'parent_id', string='Child Companies')
    name = fields.Char(string="Name", help="Name of the hospital")
    hosp_type = fields.Selection([('hospital', 'Hospital'),
                                  ('multi', 'Multi-Hospital'),
                                  ('clinic', 'Clinic'),
                                  ('community', 'Community-Health Center'),
                                  ('military', 'Military Medical Center'),
                                  ('other', 'Other')],
                                 string="Hospital Type")
    note = fields.Text('Note')
    image_129 = fields.Image(max_width=128, max_height=128)
    status = fields.Selection([('active', 'Active'),
                               ('inactive', 'Inactive')],
                              string="Hospital Status", required=True)
    hospital_seq = fields.Char(string='Hospital No.', required=True,
                              copy=False,
                              readonly=True,
                              index=True,
                              default=lambda self: 'New')
    
    parent_path = fields.Char(string="Parent Path", index=True)

    parent_id = fields.Many2one(
        comodel_name='res.partner',
        string="Parent Hospital",
        index=True,
        ondelete='cascade',
        domain="['|', ('company_id', '=', False), ('hospital_id', '=', company_id)]",
    )
    child_ids = fields.One2many(
        comodel_name='res.partner',
        inverse_name='parent_id',
        string="Hospitals",
    )
    child_count = fields.Integer(
        string="Sub Hospital Count",
        compute='_compute_child_count',
    )

    @api.depends('child_ids')
    def _compute_child_count(self):
        for partner in self:
            partner.child_count = len(partner.child_ids)
        return
    
    full_name = fields.Char(
        string="Full Name",
        compute='_compute_full_name',
        store=True,
    )
    
    @api.depends('name', 'parent_id.full_name')
    def _compute_full_name(self):
        for partner in self:
            if partner.parent_id:
                partner.full_name = "%s / %s" % (
                    partner.parent_id.full_name, partner.name)
            else:
                partner.full_name = partner.name
        return
    
 
    doctor_ids = fields.One2many('res.partner', 'hospital_id', string='Doctors')
    patient_ids = fields.One2many('res.partner', 'hospital_id', string='Patients')
    prescription_ids = fields.One2many('hospital.prescription', 'hospital_id', 'Prescriptions')
    
    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')
    
    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['hospital.prescription'].search_count(
                [('hospital_id', '=', rec.id)])
            rec.prescription_count = prescription_count
    
    @api.model
    def create(self, vals):
        # self.ensure_one()
        if vals.get('hospital_seq', 'New') == 'New':
            vals['hospital_seq'] = self.env['ir.sequence'].next_by_code(
                'hospitals.sequence') or 'New'
        result = super(Hospital, self).create(vals)
        return result
  
    def name_get(self):
        res = []
        for name in self:
            res.append((name.id, ("%s (%s)") % (name.name, name.hospital_seq)))
        return res
    
        def write(self, values):
            result = super(Practice, self).write(values)
        return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate Hospital.'))

    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'hospital.prescription',
            'domain': [('hospital_id', '=', self.id)],
            'context': {'default_hospital_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }




class HospitalRoles(models.Model):
    # : PractitionerRole/code
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _name = "hospital.roles"
    _description = "Job Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
