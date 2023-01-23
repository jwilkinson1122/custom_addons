import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class Practice(models.Model):
    _name = "podiatry.practice"
    _inherits = {
        'res.partner': 'partner_id',
    }
    _rec_name = 'practice_id'
    _order = 'sequence,id'

    # partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
    #                              help='Partner-related data of the Practice')
    
    is_practice = fields.Boolean()
    related_user_id = fields.Many2one(related='partner_id.user_id')
    prescription_count = fields.Integer(compute='get_prescription_count')
    partner_id = fields.Many2one(comodel_name='res.partner', string="Practice", required=True, ondelete='restrict')
    practitioner_id = fields.One2many(comodel_name='podiatry.practitioner', inverse_name='practice_id', string="Practitioners")

    practice_id = fields.Many2many('res.partner', domain=[('is_company', '=', True)], string="Practice", required=True)

    practice_type = fields.Selection([('hospital', 'Hospital'),
                                      ('multi', 'Multi-Hospital'),
                                      ('clinic', 'Clinic'),
                                      ('military', 'Military Medical Center'),
                                      ('other', 'Other')],
                                     string="Practice Type")
   
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
    
    child_ids = fields.One2many(
        comodel_name='podiatry.practice',
        inverse_name='parent_id',
        string="Practices",
    )
    
    child_count = fields.Integer(
        string="Subpractice Count",
        compute='_compute_child_count',
    )
    
    sequence = fields.Integer(
        string="Sequence", required=True,
        default=5,
    )

    @api.depends('child_ids')
    def _compute_child_count(self):
        for practice in self:
            practice.child_count = len(practice.child_ids)
        return

    def open_practice_prescriptions(self):
        for records in self:
            return {
                'name': _('Prescription'),
                'view_type': 'form',
                'domain': [('practice', '=', records.id)],
                'res_model': 'podiatry.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_practice': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['podiatry.prescription'].search_count([('practice', '=', records.id)])
            records.prescription_count = count

    def create_practices(self):
        print('.....res')
        self.is_practice = True
        if len(self.partner_id.user_ids):
            raise UserError(_('User for this practice already created.'))
        else:
            self.create_users_button = False
        practice_id = []
        practice_id.append(self.env['res.groups'].search([('name', '=', 'Practices')]).id)
        practice_id.append(self.env['res.groups'].search([('name', '=', 'Internal User')]).id)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Name ',
            'view_mode': 'form',
            'view_id': self.env.ref("practice.view_create_user_wizard_form").id,
            'target': 'new',
            'res_model': 'res.users',
            'context': {'default_partner_id': self.partner_id.id, 'default_is_practice': True,
                        'default_groups_id': [(6, 0, practice_id)]}
        }



