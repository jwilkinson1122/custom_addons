# -*- coding: utf-8 -*-

from odoo import fields, models, _


class Alias(models.Model):
    _inherit = 'mail.alias'

    alias_contact = fields.Selection(selection_add=[
        ('practitioners', 'Authenticated Practitioners'),
    ], ondelete={'practitioners': 'cascade'})

    def _get_alias_contact_description(self):
        if self.alias_contact == 'practitioners':
            return _('addresses linked to registered practitioners')
        return super(Alias, self)._get_alias_contact_description()
