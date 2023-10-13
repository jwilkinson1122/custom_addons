# -*- coding: utf-8 -*-

from email.policy import strict
from odoo import fields, models,api,_

class MassActionWizard(models.TransientModel):
    _name="customer.mass.update"
    _description="Customer Statement Mass Update"

    customer_update = fields.Selection([('add', 'Add'), ('remove', 'Remove')], string='Customer Overdue Statement Action',default="add")
    update_customers_ids=fields.Many2many('res.partner',string="Customers" ,required="1")
    statement_ids=fields.Many2many('customer.statement.config',string='Statement Mass Update')

    # update Customers
    def update_customers(self):
        if self.customer_update=='add':
            for partner in self.update_customers_ids:
                for record in self.statement_ids:
                    if partner not in record.partner_ids:
                        record.write({'partner_ids': [(4,partner.id)] })
        else:
            for partner in self.update_customers_ids:
                for record in self.statement_ids:
                    if partner in record.partner_ids:
                        record.partner_ids= [(3,partner.id)] 


class MassActionpartnerWizard(models.TransientModel):
    _name="customer.config.mass.update"
    _description="Partner Statement Mass Update"

    customer_config_update = fields.Selection([('add', 'Add'), ('remove', 'Remove')], string='Customer Overdue Statement Action',default="add")
    update_config_ids=fields.Many2many('customer.statement.config',string="Config" ,required="1")
    selected_partner_ids=fields.Many2many('res.partner',string='Selected partners')

    # Update Customers Statement Config
    def update_customers_config(self):
        if self.customer_config_update=='add':
            for record in self.update_config_ids:
                for partner in self.selected_partner_ids:
                    if partner not in record.partner_ids:
                        record.write({'partner_ids': [(4,partner.id)] })
        else:
            for record in self.update_config_ids:
                for partner in self.selected_partner_ids:
                    if partner in record.partner_ids:
                        record.partner_ids = [(3,partner.id)]





        
