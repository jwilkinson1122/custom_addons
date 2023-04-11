# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BloodDonor(models.Model):
    _name = 'blood.donor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Blood Donor'

    # Identification Details

    name = fields.Char(string="Name", )
    donor_code = fields.Char(string='Donor Code')
    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Others')], string="Gender",
                              tracking=True)
    marital_status = fields.Selection(
        [('um', 'UNMARRIED'), ('m', 'MARRIED'), ('w', 'WIDOWER'), ('d', 'DIVORCED'), ('x', 'SEPERATED'), ('w', 'WIDOW'),
         ('o', 'OTHERS'), ('un', 'UNKNOWN')], string='Marital Status', tracking=True)
    religion = fields.Selection(
        [('select', 'Select Religion'), ('AIND', 'ANGLO INDIAN'), ('CHR', 'CHRISTIAN'), ('HIN', 'HINDU'),
         ('JAI', 'JAIN'), ('JEW', 'JEW'), ('MUS', 'MUSLIM'), ('NEB', 'NEO-BUDDHIST'), ('OTH', 'OTHERS'),
         ('PAR', 'PARSI'), ('SIK', 'SIKH'), ('UN', 'UNKNOWN')], string="Religion", tracking=True)
    aadhaar_no = fields.Char(string="Aadhaar Number.")
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    zip = fields.Char(string='Street2')
    city = fields.Char(string='Street2')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    product_id = fields.Many2one('product.product', string='Blood Type(Group)')
    email = fields.Char(string="Email")
    mobile = fields.Char(string="Mobile")
    weight = fields.Float(string="Weight")
    camp_ids = fields.One2many('blood.donation.camp', 'donor_id', string='Camp')

    @api.model
    def create(self, vals):
        vals['donor_code'] = self.env['ir.sequence'].next_by_code('blood.donor') or 'New'
        return super(BloodDonor, self).create(vals)


class BloodDonationCamp(models.Model):
    _name = 'blood.donation.camp'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Blood Donation Camp'

    name = fields.Char(string='Name', tracking=True)
    donor_id = fields.Many2one('blood.donor', string='Donor')
    date = fields.Date(string='Date')
    last_date = fields.Date(string='Last Donation Date')
    weight = fields.Float(string="Weight")
    product_id = fields.Many2one('product.product', string='Blood Type(Group)')
    place = fields.Char(string='Place')
    report = fields.Text(string='Report')
    state = fields.Selection([('draft', 'draft'), ('test', 'Test'), ('done', 'Done'), ('reject', 'Reject')],
                             default='draft', string='State')
    picking_id = fields.Many2one('stock.picking', string='Incoming Shipment')

    def action_test(self):
        for rec in self:
            rec.state = 'test'

    def action_reject(self):
        form_id = self.env.ref('hospital_management_app.view_blood_camp_reject').id
        return {'type': 'ir.actions.act_window',
                'name': _('Camp Reject'),
                'res_model': 'blood.camp.reject',
                'view_mode': ' form',
                'views': [(form_id, 'form')],
                'context': {
                    'default_camp_id': self.id,
                },
                'target': 'new'
                }

    def action_done(self):
        for rec in self:
            picking_line = {'name': rec.name,
                            'product_id': rec.product_id.id,
                            'product_uom_qty': 1,
                            'reserved_availability': 1,
                            'quantity_done': 1,
                            'product_uom': rec.product_id.uom_id.id}
            picking_type_id = self.env.ref('stock.picking_type_in')
            location_id = self.env.ref('stock.stock_location_suppliers')
            location_dest_id = self.env.ref('stock.stock_location_stock')
            # picking depend on delivery picking type
            picking_data = {'move_ids_without_package': [(0, 0, picking_line)],
                            'picking_type_id': picking_type_id.id,
                            'state': 'draft',
                            'origin': self.name,
                            'location_id': location_id.id,
                            'location_dest_id': location_dest_id.id,
                            }
            picking_id = self.env['stock.picking'].create(picking_data)
            if picking_id:
                picking_id.action_confirm()
                picking_id.button_validate()
                rec.state = 'done'
                rec.report = 'Test is Positive'
                rec.picking_id = picking_id

    @api.onchange('donor_id')
    def onchange_donor_id(self):
        for rec in self:
            rec.product_id = rec.donor_id.product_id
            rec.weight = rec.donor_id.weight
            if rec.donor_id.camp_ids:
                for camp_id in rec.donor_id.camp_ids:
                    # if camp_id.state == 'done':
                    rec.last_date = camp_id.date
                    # else:
                    #     rec.last_date = False
            else:
                rec.last_date = False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('blood.donation.camp') or 'New'
        return super(BloodDonationCamp, self).create(vals)
