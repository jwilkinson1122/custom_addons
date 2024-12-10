# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import ast
import logging

_logger = logging.getLogger(__name__)

class ResPartnerCustomSerial(models.Model):

    _inherit = "res.partner"

    partner_type = fields.Selection([
        ('client', 'Client'),
        ('vendor', 'Vendor'),
        ('other', 'Other')], string="Partner Type", required=False, default="client")
    
    customer_number = fields.Char(string="Partner Serial", required=False, copy=False, readonly=True, index=True, default=lambda self: False)

    @api.model
    def create(self, vals):  # save button in the form view
        """ 
        """
        if vals.get('customer_number', False) == False:
            if vals.get('partner_type', False):
                # added to account for partner_type
                if vals['partner_type'] == 'client':
                    vals['customer_number'] = self.env['ir.sequence'].next_by_code('res.partner.client.custom.serial') or _('New')
                elif vals['partner_type'] == 'vendor':
                    print("vendor")
                    vals['customer_number'] = self.env['ir.sequence'].next_by_code('res.partner.vendor.custom.serial') or _('New')
                else:
                    pass
        return super(ResPartnerCustomSerial, self).create(vals)
    
    def write(self, vals):
        if 'partner_type' in vals:

            if vals['partner_type'] != self.partner_type:

                if vals['partner_type'] == 'client':
                    new_serial = self.env['ir.sequence'].next_by_code('res.partner.client.custom.serial') or _('New')
                    self.write({'customer_number': new_serial})
                elif vals['partner_type'] == 'vendor':
                    new_serial = self.env['ir.sequence'].next_by_code('res.partner.vendor.custom.serial') or _('New')
                    self.write({'customer_number': new_serial})
            else:
                pass
        return super(ResPartnerCustomSerial, self).write(vals)

    def unlink(self):
        if self['partner_type'] == 'client':
            partner_stored_data = self.env['res.partner'].sudo().search([('partner_type', '=', 'client'), ('id', '>', self.id)])
            if not partner_stored_data:
                sequence_stored_data = self.env['ir.sequence'].sudo().search([('code', '=', 'res.partner.client.custom.serial')])
                if sequence_stored_data.number_next_actual > 1:
                    sequence_stored_data.number_next_actual -= 1
        elif self['partner_type'] == 'vendor':
            partner_stored_data = self.env['res.partner'].sudo().search([('partner_type', '=', 'vendor'), ('id', '>', self.id)])
            if not partner_stored_data:
                sequence_stored_data = self.env['ir.sequence'].sudo().search([('code', '=', 'res.partner.vendor.custom.serial')])
                if sequence_stored_data.number_next_actual > 1:
                    sequence_stored_data.number_next_actual -= 1
        else:
            pass
        
        return super(ResPartnerCustomSerial, self).unlink()


class ProjectAnalyticAccount(models.Model):
    _inherit = "project.project"

    def action_view_tasks(self):
        action = self.env['ir.actions.act_window'].with_context({'active_id': self.id})._for_xml_id('project.act_project_project_2_project_task_all')
        action['display_name'] = _("%(name)s", name=self.name)
        context = action['context'].replace('active_id', str(self.id))
        context = ast.literal_eval(context)
        context.update({
            'create': self.active,
            'active_test': self.active
            })
        action['context'] = context


        vals = {
            'name': "Projects",
            'default_applicability': "optional",
            'color': 3,
            'company_id': self.env.company.id,
        }
        
        analytic_plan_stored_data = self.env['account.analytic.plan'].sudo().search([('name', '=', 'Projects')], limit=1)
        if analytic_plan_stored_data:
            pass
        else:
            analytic_plan_stored_data.create(vals)
        self.env.cr.commit()


        vals = {
            'name': self.name,
            'partner_id': self.partner_id.id,
            # 'code': ,
            'plan_id': analytic_plan_stored_data.id,
            'company_id': self.env.company.id,
            'currency_id': self.env.company.currency_id.id,
        }
        
        analytic_account_stored_data = self.env['account.analytic.account'].sudo().search([('name', '=', self.name)], limit=1)
        if analytic_account_stored_data:
            pass
        else:
            new_account = self.env['account.analytic.account'].sudo().create(vals)
            self.env.cr.commit()
            self.analytic_account_id = new_account.id

        return action

class PurchaseOrderWithAnalyticAppliedToLines(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "analytic.mixin"]

    analytic_distribution = fields.Json(
        inverse="_inverse_analytic_distribution",
    )

    @api.depends("order_line.analytic_distribution")
    def _compute_analytic_distribution(self):
        """If all order line have same analytic distribution set analytic_distribution.
        If no lines, respect value given by the user.
        """
        for po in self:
            if po.order_line:
                al = po.order_line[0].analytic_distribution or False
                for ol in po.order_line:
                    if ol.analytic_distribution != al:
                        al = False
                        break
                po.analytic_distribution = al

    def _inverse_analytic_distribution(self):
        """When set analytic_distribution set analytic distribution on all order lines"""
        for po in self:
            if po.analytic_distribution:
                po.order_line.write({"analytic_distribution": po.analytic_distribution})

    @api.onchange("analytic_distribution")
    def _onchange_analytic_distribution(self):
        """When change analytic_distribution set analytic distribution on all order lines"""
        if self.analytic_distribution:
            self.order_line.update(
                {"analytic_distribution": self.analytic_distribution}
            )
