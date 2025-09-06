# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    helpdesk_tickets_ids = fields.Many2many(
        "helpdesk.ticket", string="Helpdesk Tickets"
    )
    helpdesk_tickets_count = fields.Integer(
        string="# of Delivery Order", compute="_get_helpdesk_tickets_count"
    )

    @api.depends("helpdesk_tickets_ids")
    def _get_helpdesk_tickets_count(self):
        for rec in self:
            rec.helpdesk_tickets_count = len(rec.helpdesk_tickets_ids)

    def helpdesk_ticket(self):
        action = self.env.ref("helpdesk.helpdesk_ticket_action_main_tree").read()[0]

        tickets = self.order_line.mapped("helpdesk_discription_id")
        if len(tickets) > 1:
            action["domain"] = [("id", "in", tickets.ids)]
        elif tickets:
            action["views"] = [
                (self.env.ref("helpdesk.helpdesk_ticket_view_form").id, "form")
            ]
            action["res_id"] = tickets.id
        return action

    # Overwrite Confirm Button
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped("state")):
            raise UserError(
                _("It is not allowed to confirm an order in the following states: %s")
                % (", ".join(self._get_forbidden_state_confirm()))
            )

        for order in self.filtered(
            lambda order: order.partner_id not in order.message_partner_ids
        ):
            order.message_subscribe([order.partner_id.id])
        self.write({"state": "sale", "date_order": fields.Datetime.now()})
        self._action_confirm()
        if self.env.user.has_group("sale.group_auto_done_setting"):
            self.action_done()
        # -------------------------Start-----------------------------#
        helpdesk_ticket_dict = {}
        helpdesk_ticket_list = []
        for line in self.order_line:
            if line:
                if line.product_id.is_helpdesk:
                    helpdesk_ticket_dict = {
                        "name": line.product_id.name,
                        "team_id": line.product_id.helpdesk_team.id,
                        "user_id": line.product_id.helpdesk_assigned_to.id,
                        "partner_id": self.partner_id.id,
                        "partner_name": self.partner_id.name,
                        "partner_email": self.partner_id.email,
                        "description": line.name,
                    }
                    helpdesk_ticket_id = self.env["helpdesk.ticket"].create(
                        helpdesk_ticket_dict
                    )
                    if helpdesk_ticket_id:
                        line.helpdesk_discription_id = helpdesk_ticket_id.id
                        helpdesk_ticket_list.append(helpdesk_ticket_id.id)
                        self.helpdesk_tickets_ids = helpdesk_ticket_list

        # -------------------------End-----------------------------#
        return True


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    helpdesk_discription_id = fields.Many2one("helpdesk.ticket", string="Helpdesk")
