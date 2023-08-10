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
    _inherits = {'res.partner': 'partner_id'}

    _rec_name = 'practice_id'
    _order = 'sequence,id'

    user_id = fields.Many2one(comodel_name='res.users', string="Created by")
    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='cascade', help='Partner-related data of the Practice')
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )
    
    practice_id = fields.Many2one('res.partner',domain=[('is_practice','=',True)],string='Practice')
    practitioner_ids = fields.Many2many('podiatry.practitioner', 'practice_practitioner_rel', string='Practitioners')
    patient_ids = fields.Many2many('podiatry.patient', 'practice_patient_rel', string='Patients')

    prescription_ids = fields.One2many("podiatry.prescription", 'practice_id', string="Practice Prescriptions", domain=[("active", "=", True)])
    practice_type_id = fields.Many2one(string='Practice Type', comodel_name='podiatry.practice.type')
    active = fields.Boolean(string="Active", default=True, tracking=True)
    color = fields.Integer(string="Color Index (0-15)")
    sequence = fields.Integer(string="Sequence", required=True, default=5)
    code = fields.Char(string="Code", copy=False)
    identification = fields.Char(string="Identification", index=True)
    reference = fields.Char(string='Practice Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    notes = fields.Text(string="Notes")
    # full_name = fields.Char(string="Full Name", compute='_compute_full_name', store=True)
    partner_relation_label = fields.Char('Partner relation label', translate=True, default='Attached To:', readonly=True)
    practice_rel_type = fields.Selection([('parent', 'Parent'), ('child', 'Child')], 'Company Type', required=True, default='parent')

    # @api.depends('name', 'parent_id.full_name')
    # def _compute_full_name(self):
    #     for practice in self:
    #         if practice.parent_id:
    #             practice.full_name = "%s / %s" % (
    #                 practice.parent_id.full_name, practice.name)
    #         else:
    #             practice.full_name = practice.name
    #     return
    
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
            
    practice_address_id = fields.Many2one('res.partner', string="Address", )

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
        
    def unlink(self):
        self.partner_id.unlink()
        return super(Practice, self).unlink()