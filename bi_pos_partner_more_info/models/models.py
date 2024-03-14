# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    allow_custom_fields = fields.Boolean(string='Show Custom Partner Information')
    show_custom_field = fields.Many2many('custom.field', string='Show Custom Partner Information')

    @api.onchange('allow_custom_fields')
    def _onchange_allow_custom_fields(self):
        if not self.allow_custom_fields:
            self.show_custom_field = False


class CustomField(models.Model):
    _name = "custom.field"

    name = fields.Char(string=" Custom Fields")
    config_id = fields.Many2one("pos.config", string="Pos Config")


class InheritPartner(models.Model):
    _inherit = "res.partner"

    info_ids = fields.One2many('res.partner.info', 'partner_id', string="More Info")

    @api.model
    def create_from_ui(self, partner, extraPartner):
        """ create or modify a partner from the point of sale ui.
            partner contains the partner's fields. """
        # image is a dataurl, get the data after the comma
        extraPartner_id = partner.pop('id', False)
        if extraPartner:
            if extraPartner.get('image_1920'):
                extraPartner['image_1920'] = extraPartner['image_1920'].split(',')[1]
            if extraPartner_id:  # Modifying existing extraPartner
                custom_info = self.env['custom.field'].search([])
                for i in custom_info:
                    if i.name in extraPartner.keys():
                        info_data = self.env['res.partner.info'].search(
                            [('partner_id', '=', extraPartner_id), ('name', '=', i.name)])
                        if info_data:
                            info_data.write({'info_name': extraPartner[i.name], 'partner_id': extraPartner_id})
                        else:
                            self.browse(extraPartner_id).write(
                                {'info_ids': [(0, 0, {'name': i.name, 'info_name': extraPartner[i.name]})]})
            else:
                extraPartner_id = self.create(extraPartner).id

        if partner:
            if partner.get('image_1920'):
                partner['image_1920'] = partner['image_1920'].split(',')[1]
            if extraPartner_id:  # Modifying existing partner

                self.browse(extraPartner_id).write(partner)
            else:
                extraPartner_id = self.create(partner).id
        return extraPartner_id


class ResPartnerInfo(models.Model):
    _name = "res.partner.info"

    name = fields.Char(string="Extra Info", required=True)
    info_name = fields.Char(string="Info Name")
    partner_id = fields.Many2one("res.partner", string="Partner Info")
    field_id = fields.Many2one("custom.field", string="Custom Filed")
