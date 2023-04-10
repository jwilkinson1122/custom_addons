# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class InheritedSaleOrder(models.Model):
    _inherit = 'sale.order'

    prescription_id = fields.Many2one('podiatry.prescription', readonly=True) 
    practice_id = fields.Char(related='prescription_id.practice_id.name')
    practitioner_id = fields.Char(
        related='prescription_id.practitioner_id.name')
    patient_id = fields.Char(related='prescription_id.patient_id.name')
    prescription_date = fields.Date(
        related='prescription_id.prescription_date')
    purchase_order_count = fields.Char()
    po_ref = fields.Many2one('purchase.order', string='PO Ref')
    helpdesk_tickets_ids = fields.Many2many('helpdesk.ticket',string='Helpdesk Tickets')
    helpdesk_tickets_count = fields.Integer(string='# of Delivery Order', compute='_get_helpdesk_tickets_count')

    def print_prescription_report_ticket_size(self):
        return self.env.ref("podiatry.practitioner_prescription_ticket_size2").report_action(self.prescription_id)

    def print_podiatry_prescription_report_ticket_size(self):
        return self.env.ref("podiatry.practitioner_prescription_podiatry_ticket_size2").report_action(self.prescription_id)

    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(
                rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(
        string="This sale order is approved for the sum of: ", compute='_compute_amount_in_word')

    def print_sale_order_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "podiatry.sale_order_report",
            'report_file': "podiatry.sale_order_report",
            'report_type': 'qweb-pdf',
        }

    def print_prescription_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "podiatry.sale_prescription_template",
            'report_file': "podiatry.sale_prescription_template",
            'report_type': 'qweb-pdf'
        }

    def print_prescription_report(self):
        pass

    def print_prescription_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "podiatry.sale_prescription_template",
            'report_file': "podiatry.sale_prescription_template",
            'report_type': 'qweb-pdf'
        }
        
    @api.depends('helpdesk_tickets_ids')
    def _get_helpdesk_tickets_count(self):
        for rec in self:
            rec.helpdesk_tickets_count = len(rec.helpdesk_tickets_ids)

    def helpdesk_ticket(self):
        action = self.env.ref('helpdesk.helpdesk_ticket_action_main_tree').read()[0]

        tickets = self.order_line.mapped('helpdesk_description_id')
        if len(tickets) > 1:
            action['domain'] = [('id', 'in', tickets.ids)]
        elif tickets:
            action['views'] = [(self.env.ref('helpdesk.helpdesk_ticket_view_form').id, 'form')]
            action['res_id'] = tickets.id
        return action

    # Overwrite Confirm Button
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        helpdesk_ticket_dict = {}
        helpdesk_ticket_list = []
        for line in self.order_line:
            if line:
                if line.product_id.is_helpdesk:
                    helpdesk_ticket_dict = {
                                            'name' : line.product_id.name,
                                            'team_id' : line.product_id.helpdesk_team.id,
                                            'user_id' : line.product_id.helpdesk_assigned_to.id,
                                            'partner_id' : self.partner_id.id,
                                            'partner_name' : self.partner_id.name,
                                            'partner_email' : self.partner_id.email,
                                            'description' : line.name  
                                           }
                    helpdesk_ticket_id = self.env['helpdesk.ticket'].create(helpdesk_ticket_dict)
                    if helpdesk_ticket_id:
                        line.helpdesk_description_id = helpdesk_ticket_id.id
                        helpdesk_ticket_list.append(helpdesk_ticket_id.id)
                        self.helpdesk_tickets_ids = helpdesk_ticket_list
        return True


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    helpdesk_description_id = fields.Many2one('helpdesk.ticket',string='Helpdesk')


    @api.model
    def _prepare_from_pos(self, sale_order, order_line_data):
        ProductProduct = self.env["product.product"]
        product = ProductProduct.browse(order_line_data["product_id"])
        return {
            "order_id": sale_order.id,
            "product_id": order_line_data["product_id"],
            "name": product.name,
            "product_uom_qty": order_line_data["qty"],
            "discount": order_line_data["discount"],
            "price_unit": order_line_data["price_unit"],
            "tax_id": order_line_data["tax_ids"],
        }


