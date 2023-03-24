import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

from . import practice

# from lxml import etree
# added import statement in try-except because when server runs on
# windows operating system issue arise because this library is not in Windows.
try:
    from odoo.tools import image_colorize
except:
    image_colorize = False


class Practitioner(models.Model):
    _name = "podiatry.practitioner"
    _inherits = {
        'res.partner': 'partner_id',
    }
    create_users_button = fields.Boolean()

    partner_id = fields.Many2one('res.partner', string='Related Partner', domain=("is_company", "=", False), required=True, ondelete='restrict',
                                 help='Partner-related data of the Practice')
    
    is_practitioner = fields.Boolean()
    related_user_id = fields.Many2one(related='partner_id.user_id')
    
    practice = fields.Many2one('podiatry.practice', 'Practice', help="Practice where practitioners works")

    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_podiatry_prescriptions(self):
        for records in self:
            return {
                'name': _('Practitioner Prescription'),
                'view_type': 'form',
                'res_model': 'podiatry.prescription',
                'domain': [('practitioner', '=', records.id)],
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_practitioner': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['podiatry.prescription'].search_count([('practitioner', '=', records.id)])
            records.prescription_count = count

    def create_practitioners(self):
        print('.....res')
        self.is_practitioner = True
        if len(self.partner_id.user_ids):
            raise UserError(_('User for this patient already created.'))
        else:
            self.create_users_button = False
        practitioner_id = []
        practitioner_id.append(self.env['res.groups'].search([('name', '=', 'Practitioners')]).id)
        practitioner_id.append(self.env['res.groups'].search([('name', '=', 'Internal User')]).id)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Name ',
            'view_mode': 'form',
            'view_id': self.env.ref("practitioner.view_create_user_wizard_form").id,
            'target': 'new',
            'res_model': 'res.users',
            'context': {'default_partner_id': self.partner_id.id, 'default_is_practitioner': True,
                        'default_groups_id': [(6, 0, practitioner_id)]}
        }



