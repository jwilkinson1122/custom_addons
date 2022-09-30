# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _


class ClinicAnimal(models.Model):
    _name = 'clinic.animal'
    _inherit = ['mail.thread']

    name = fields.Char(_('Name'))
    type = fields.Char(_('Type'))
    sex = fields.Selection((
        ('male', 'Male'),
        ('female', 'Female')
    ), _('Sex'), required=True)
    age = fields.Integer(_('Age'), track_visibility='always')
    owner_id = fields.Many2one('res.partner', domain=[('customer', '=', True)], track_visibility='always')
    owner_phone = fields.Char(related='owner_id.phone', string=_('Phone'))
    active = fields.Boolean(_('Active'), default=True, track_visibility='always')

    @api.one
    def name_get(self):
        return self.id, u'☞ ' + self.name

    @api.model
    def default_get(self, fields):
        values = super(ClinicAnimal, self).default_get(fields)
        # values['sex'] = 'male'
        return values
