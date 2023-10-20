# -*- coding: utf-8 -*-

from odoo import models, tools, _


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    def _alias_get_error_message(self, message, message_dict, alias):
        if alias.alias_contact == 'practitioners':
            email_from = tools.decode_message_header(message, 'From')
            email_address = tools.email_split(email_from)[0]
            practitioner = self.env['pod.practitioner'].search([('practice_email', 'ilike', email_address)], limit=1)
            if not practitioner:
                practitioner = self.env['pod.practitioner'].search([('user_id.email', 'ilike', email_address)], limit=1)
            if not practitioner:
                return _('restricted to practitioners')
            return False
        return super(BaseModel, self)._alias_get_error_message(message, message_dict, alias)
