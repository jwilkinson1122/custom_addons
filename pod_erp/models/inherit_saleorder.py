# -*- coding: utf-8 -*-

from odoo import api, fields, models,_


class InheritedSaleOrder(models.Model):
    _inherit = 'sale.order'

    prescription_id = fields.Many2one('practitioner.prescription', readonly=True)
    practice = fields.Char(related='prescription_id.practice.name')
    practitioner = fields.Char(related='prescription_id.practitioner.name')
    patient = fields.Char(related='prescription_id.patient.name')
    prescription_date = fields.Date(related='prescription_id.prescription_date')
    purchase_order_count = fields.Char()
    po_ref = fields.Many2one('purchase.order', string='PO Ref')
    device_type = fields.Many2one(related='prescription_id.device_type')
    
    helpdesk_tickets_ids = fields.Many2many('helpdesk.ticket',string='Helpdesk Tickets')
    helpdesk_tickets_count = fields.Integer(string='# of Delivery Order', compute='_get_helpdesk_tickets_count')
    
    def print_prescription_report_ticket_size(self):
        return self.env.ref("pod_erp.practitioner_prescription_ticket_size2").report_action(self.prescription_id)

    def print_podiatry_prescription_report_ticket_size(self):
        return self.env.ref("pod_erp.practitioner_prescription_podiatry_ticket_size2").report_action(self.prescription_id)

    def _compute_amount_in_word(self):
        for rec in self:
                rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(string="This sale order is approved for the sum of: ", compute='_compute_amount_in_word')

    def print_sale_order_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "pod_erp.sale_order_report",
            'report_file': "pod_erp.sale_order_report",
            'report_type': 'qweb-pdf',
        }

    def print_purchase_order_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "pod_erp.purchase_order_report",
            'report_file': "pod_erp.purchase_order_report",
            'report_type': 'qweb-pdf',
        }

    @api.onchange('prescription_id')
    def test(self):
        product = self.env.ref('pod_erp.pod_erp_product')
        self.order_line = None
        if self.prescription_id.eye_examination_chargeable==True:
            self.order_line |= self.order_line.new({
                'name':'',
                'product_id':product.id,
                'product_uom_qty':1,
                'qty_delivered': 1,
                'product_uom':'',
                'price_unit':'',

            })
            
    # @api.model
    # def create(self,vals):
    #     order_line_product = [(0, 0, {'product_id':30,'partner_invoice_id':12,'partner_id':12})]
    #
    #     vals = {
    #
    #         'order_line': order_line_product,
    #
    #     }
    #     result = super(InheritedSaleOrder,self).create(vals)
    #     return result

    def print_podiatry_prescription_report(self):
        pass


    def print_prescription_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "pod_erp.sale_prescription_template",
            'report_file': "pod_erp.sale_prescription_template",
            'report_type': 'qweb-pdf'
        }


    @api.depends('helpdesk_tickets_ids')
    def _get_helpdesk_tickets_count(self):
        for rec in self:
            rec.helpdesk_tickets_count = len(rec.helpdesk_tickets_ids)

    def helpdesk_ticket(self):
        action = self.env.ref('helpdesk.helpdesk_ticket_action_main_tree').read()[0]

        tickets = self.order_line.mapped('helpdesk_discription_id')
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
                        line.helpdesk_discription_id = helpdesk_ticket_id.id
                        helpdesk_ticket_list.append(helpdesk_ticket_id.id)
                        self.helpdesk_tickets_ids = helpdesk_ticket_list
        return True



class InheritedSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    helpdesk_discription_id = fields.Many2one('helpdesk.ticket',string='Helpdesk')






