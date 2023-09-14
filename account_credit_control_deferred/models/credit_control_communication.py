# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class CreditControlCommunication(models.Model):
    _inherit = "credit.control.communication"

    state = fields.Selection(
        [
            ("queued", "Queued"),
            ("sent", "Sent"),
            ("email_error", "Error"),
            ("solved", "Solved"),
        ],
        readonly=True,
        required=True,
        default="queued",
    )
    total_current_invoiced = fields.Float(compute="_compute_total", store=True)
    last_message = fields.Datetime(compute="_compute_last_message", store=True)
    total_invoiced = fields.Float(store=True)
    total_due = fields.Float(store=True)

    @api.depends("message_ids")
    def _compute_last_message(self):
        for record in self:
            record.last_message = max(
                record.message_ids.mapped("date") + [record.write_date]
            )

    def _compute_total(self):
        super()._compute_total()
        for communication in self:
            communication.total_current_invoiced = communication._get_current_total()

    def _get_current_total(self):
        result = 0
        for line in self.credit_control_line_ids:
            if line.balance_due > 0:
                result += line.amount_due
        return result

    def action_mark_as_sent(self):
        self.ensure_one()
        self.credit_control_line_ids.filtered(
            lambda line: line.state == "queued"
        ).write({"state": "sent"})
        self.write(self._sent_vals())

    def _sent_vals(self):
        return {"state": "sent"}

    def action_mark_as_solved(self):
        self.write(self._solved_vals())

    def _solved_vals(self):
        return {"state": "solved"}

    def action_communication_answer(self):
        self.ensure_one()
        ir_model_data = self.env["ir.model.data"]
        template_id = self.policy_level_id.email_template_id.id
        try:
            compose_form_id = ir_model_data.get_object_reference(
                "mail", "email_compose_message_wizard_form"
            )[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.pop("active_id", False)
        ctx.pop("active_ids", False)
        ctx.pop("active_model", False)
        ctx.update(
            {
                "default_model": self._name,
                "default_res_id": self.ids[0],
                "default_use_template": False,
                "default_template_id": template_id,
                "default_composition_mode": "mass_post",
                "default_is_log": False,
                "default_notify": True,
                "force_email": True,
            }
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }

    def action_communication_send(self):
        self.ensure_one()
        ir_model_data = self.env["ir.model.data"]
        template_id = self.policy_level_id.email_template_id.id
        try:
            compose_form_id = ir_model_data.get_object_reference(
                "mail", "email_compose_message_wizard_form"
            )[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.pop("active_id", False)
        ctx.pop("active_ids", False)
        ctx.pop("active_model", False)
        ctx.update(
            {
                "default_model": self._name,
                "default_res_id": self.ids[0],
                "default_use_template": bool(template_id),
                "default_template_id": template_id,
                "default_composition_mode": "mass_post",
                "default_is_log": False,
                "default_notify": True,
                "default_subtype_id": self.env.ref(
                    "account_credit_control.mt_request"
                ).id,
                "force_email": True,
                "mark_communication_as_sent": True,
            }
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get("mark_communication_as_sent"):
            self.filtered(lambda o: o.state in ["queued", "email_error"]).write(
                {"state": "sent"}
            )
        return super().message_post(**kwargs)

    @api.model
    def _aggregate_credit_lines(self, lines):
        result = super()._aggregate_credit_lines(lines)
        partner_obj = self.env["res.partner"]
        for res in result:
            partner = partner_obj.browse(res["partner_id"])
            if partner.credit_control_contact_partner_id:
                res["contact_address_id"] = partner.credit_control_contact_partner_id.id
        return result

    def update_balance(self):
        for record in self:
            record.credit_control_line_ids._update_balance(record.currency_id)

    def _onchange_partner_id(self):
        data = super()._onchange_partner_id()
        for record in self:
            if (
                record.company_id.payment_responsible_id
                or record.partner_id.payment_responsible_id
            ):
                record.user_id = (
                    record.partner_id.payment_responsible_id
                    or record.company_id.payment_responsible_id
                )
        return data

    def _generate_comm_from_credit_lines(self, lines):
        comms = super()._generate_comm_from_credit_lines(lines)
        for comm in comms:
            comm.message_subscribe([comm.user_id.partner_id.id])
        return comms
