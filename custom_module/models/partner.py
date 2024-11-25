import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    primary_address = fields.Boolean()

    def set_primary_address_if_none(self, parent_id):
        primary_adress_records = self.env['res.partner'].search([
            ('parent_id', '=', parent_id.id),
            ('type', '=', 'delivery'),
            ('primary_address', '=', True)])
        if not primary_adress_records:
            primary_record = self.env['res.partner'].search([
                ('type', '=', 'delivery'),
                ('parent_id', '=', parent_id.id)], limit=1)
            primary_record.primary_address = True

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.type == 'delivery' and res.parent_id:
            primary_adress_records = self.env['res.partner'].search([
                ('parent_id', '=', res.parent_id.id),
                ('id', '!=', res.id),
                ('type', '=', 'delivery'),
                ('primary_address', '=', True)])
            if res.primary_address and primary_adress_records:
                for primary_adress_record in primary_adress_records:
                    primary_adress_record.primary_address = False
                return res
            if not res.primary_address and not primary_adress_records:
                res.primary_address = True
        return res

    def write(self, vals):
        res = super().write(vals)
        if self.primary_address and self.parent_id:
            if vals.get('primary_address'):
                primary_adress_records = self.env['res.partner'].search([
                    ('parent_id', '=', self.parent_id.id),
                    ('id', '!=', self.id),
                    ('type', '=', 'delivery'),
                    ('primary_address', '=', True)])
                for primary_adress_record in primary_adress_records:
                    primary_adress_record.primary_address = False
        self.set_primary_address_if_none(self.parent_id)
        return res

    def unlink(self):
        for obj in self:
            if obj.primary_address and obj.parent_id:
                parent_id = obj.parent_id
                res = super(ResPartner, obj).unlink()
                self.set_primary_address_if_none(parent_id)
                return res
