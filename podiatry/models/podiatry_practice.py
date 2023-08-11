import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

import logging

_logger = logging.getLogger(__name__)


class Practice(models.Model):
    _name = 'podiatry.practice'
    _description = "Medical Practice"
    _inherit = ['mail.thread',
                'mail.activity.mixin', 'image.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }

    _rec_name = 'practice_id'
    _order = 'sequence,id'

    _parent_name = 'parent_id'
    _parent_store = True

    parent_path = fields.Char(string="Parent Path", index=True)

    parent_id = fields.Many2one(
        comodel_name='podiatry.practice',
        string="Practice",
        index=True,
        ondelete='cascade',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    
    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='cascade',
                                 help='Partner-related data of the Practice')

    active = fields.Boolean(string="Active", default=True, tracking=True)
    # name = fields.Char(string="Practice Name", index=True, translate=True)
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
    reference = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))

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

    user_id = fields.Many2one(comodel_name='res.users', string="Created by")
    practice_id = fields.Many2many('res.partner', domain=[('is_practice', '=', True)], string="Practice", required=True)
    practice_type_id = fields.Many2one(string='Practice Type', comodel_name='podiatry.practice.type')
    
    practice_rel_type = fields.Selection([
        ('parent', 'Parent'),
        ('child', 'Child'),
    ], 'Company Type', required=True, default='parent')
    
    partner_relation_label = fields.Char('Partner relation label', translate=True, default='Attached To:', readonly=True)
    
    practitioner_ids = fields.One2many(
        string='Practitioners',
        comodel_name='podiatry.practitioner',
        inverse_name='practice_id',
        compute='_compute_practitioner_count',
    )
    
    practitioner_count = fields.Integer(string='Practitioner Count', compute='_compute_practitioner_count')
    
    def _compute_practitioner_count(self):
        for record in self:
            practitioners = self.env['podiatry.practitioner'].search([
                ('practice_id', 'child_of', record.id),
            ])
            record.practitioner_count = len(practitioners)
            record.practitioner_ids = [(6, 0, practitioners.ids)]

    patient_ids = fields.One2many(
        string='Patients',
        comodel_name='podiatry.patient',
        inverse_name='practice_id',
        compute='_compute_patient_count',
    )
    
    patient_count = fields.Integer(string='Patient Count', compute='_compute_patient_count')
    
    def _compute_patient_count(self):
        for record in self:
            patients = self.env['podiatry.patient'].search([
                ('practice_id', 'child_of', record.id),
            ])
            record.patient_count = len(patients)
            record.patient_ids = [(6, 0, patients.ids)]

    # practice_prescription_id = fields.One2many(
    #     comodel_name='podiatry.prescription',
    #     inverse_name='practice_id',
    #     string="Prescriptions",
    # )
    
    practice_prescription_id = fields.One2many(
        "podiatry.prescription",
        "practice_id",
        string="Practice Prescriptions",
        domain=[("active", "=", True)],
    )
    
    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')


    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['podiatry.prescription'].search_count(
                [('practice_id', '=', rec.id)])
            rec.prescription_count = prescription_count
            
        
    @api.onchange('practice_id')
    def _onchange_practice(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.practice_id
        self.practice_address_id = address_id
        
    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    def unlink(self):
        self.partner_id.unlink()
        return super(Practice, self).unlink()

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

    practice_address_id = fields.Many2one('res.partner', string="Address", )

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

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'podiatry', 'static/src/img', 'company_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.model
    def create(self, vals):
        if not vals.get('notes'):
            vals['notes'] = 'Practice Notes'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'podiatry.practice') or _('New')
        practice = super(Practice, self).create(vals)
        return practice

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            result.append((rec.id, name))
        return result
    
    def write(self, values):
        result = super(Practice, self).write(values)
        return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate practice.'))

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
        
    # def action_open_practitioners(self):
    #         return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Practitioners',
    #         'res_model': 'podiatry.practitioner',
    #         'domain': [('practice_id', '=', self.id)],
    #         'context': {'default_practice_id': self.id},
    #         'view_mode': 'kanban,tree,form',
    #         'target': 'current',
    #     }
            
    # def action_open_patients(self):
    #         return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Patients',
    #         'res_model': 'podiatry.patient',
    #         'domain': [('practice_id', '=', self.id)],
    #         'context': {'default_practice_id': self.id},
    #         'view_mode': 'kanban,tree,form',
    #         'target': 'current',
    #     }
            
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


 