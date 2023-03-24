import base64
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

class Practice(models.Model):
    _name = "podiatry.practice"
    _inherit = ['mail.thread',
                'mail.activity.mixin', 'image.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }
    _rec_name = 'reference'
    _order = 'sequence,id'
    _parent_name = 'parent_id'
    _parent_store = True
    
    
    sequence = fields.Integer(
        string="Sequence", required=True,
        default=5,
    )

    code = fields.Char(string="Code", copy=False)
    # reference = fields.Char("Practice Number", readonly=True, index=True, default="New")
    reference = fields.Char(required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    # practice_id = fields.Many2many('res.partner', domain=[('is_practice', '=', True)], string="Practice", required=True)
    partner_id = fields.Many2one('res.partner', string='Related Partner', domain=("is_company", "=", True), required=True, help='Partner-related data of the Practice')
    active = fields.Boolean(string="Active", default=True, tracking=True)
    notes = fields.Text(string="Notes")
    image_129 = fields.Image(max_width=128, max_height=128)
    is_practice = fields.Boolean()
    practice_type = fields.Selection([('hospital', 'Hospital'),
                                      ('multi', 'Multi-Hospital'),
                                      ('clinic', 'Clinic'),
                                      ('military', 'VA Medical Center'),
                                      ('other', 'Other')],
                                     string="Practice Type")
    
    # create_users_button = fields.Boolean()
    
  
    prescription_ids = fields.One2many('podiatry.prescription', 'practice', string='Practice Prescriptions')
    
    prescription_count = fields.Integer(compute='get_prescription_count')
    
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

    @api.depends('child_ids')
    def _compute_child_count(self):
        for practice in self:
            practice.child_count = len(practice.child_ids)
        return
    
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
    
    def unlink(self):
        self.partner_id.unlink()
        return super(Practice, self).unlink()
    
    
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
            'pod_erp', 'static/src/img', 'company_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)
    
    @api.model
    def create_practices(self, vals):
        if not vals.get('notes'):
            vals['notes'] = 'New Practice'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'podiatry.practice.sequence') or _('New')
        practice = super(Practice, self).create(vals)
        return practice
    
    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('podiatry.prescription.sequence')
    #     result = super(Prescription, self).create(vals)
    #     return result

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.reference + '] ' + rec.name
            result.append((rec.id, name))
        return result

    def write(self, values):
        result = super(Practice, self).write(values)
        return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate practice.'))
    
   
    def get_prescription_count(self):
        for records in self:
            count = self.env['podiatry.prescription'].search_count([('practice', '=', records.id)])
            records.prescription_count = count
            
    
    def open_practice_prescriptions(self):
        for records in self:
            return {
                'name': _('Practice Prescription'),
                'view_type': 'form',
                'res_model': 'podiatry.prescription',
                'domain': [('practice', '=', records.id)],
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_practice': self.id},
                'type': 'ir.actions.act_window',
            }
            
    
 
    # def create_practices(self, vals):
    #     print("Practice create vals ",vals)
    #     self.is_practice = True
    #     if len(self.partner_id):
    #         raise UserError(_('Partner already created.'))
    #     else:
    #         self.create_users_button = False
    #     practice_id = []
    #     practice_id.append(self.env['res.groups'].search([('name', '=', 'Practices')]).id)
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Name ',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref("practice.view_create_user_wizard_form").id,
    #         'target': 'new',
    #         'res_model': 'res.users',
    #         'context': {'default_partner_id': self.partner_id.id, 'default_is_practice': True,
    #                     'default_groups_id': [(6, 0, practice_id)]}
    #     }


 