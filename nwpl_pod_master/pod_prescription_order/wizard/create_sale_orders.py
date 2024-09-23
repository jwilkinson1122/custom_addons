from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class PrescriptionOrderWizard(models.TransientModel):
    _name = "prescription.order.wizard"
    _description = "Prescription order wizard"

    @api.model
    def _default_order(self):
        # in case the cron hasn't run
        self.env["prescription.order"].expire_orders()
        if not self.env.context.get("active_id"):
            return False
        prescription_order = self.env["prescription.order"].search(
            [("id", "=", self.env.context["active_id"])], limit=1
        )
        if prescription_order.state == "expired":
            raise UserError(
                _("You can't create a sale order from " "an expired prescription order!")
            )
        return prescription_order

    @api.model
    def _check_valid_prescription_order_line(self, rx_lines):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        company_id = False

        if all(
            float_is_zero(line.remaining_uom_qty, precision_digits=precision)
            for line in rx_lines
        ):
            raise UserError(_("The sale has already been completed."))

        for line in rx_lines:
            if line.order_id.state != "open":
                raise UserError(
                    _("Prescription Order %s is not open") % line.order_id.name
                )
            line_company_id = line.company_id and line.company_id.id or False
            if company_id is not False and line_company_id != company_id:
                raise UserError(_("You have to select lines " "from the same company."))
            else:
                company_id = line_company_id

    @api.model
    def _default_lines(self):
        prescription_order_line_obj = self.env["prescription.order.line"]
        prescription_order_line_ids = self.env.context.get("active_ids", False)
        active_model = self.env.context.get("active_model", False)

        if active_model == "prescription.order":
            rx_lines = self._default_order().line_ids
        else:
            rx_lines = prescription_order_line_obj.browse(prescription_order_line_ids)

        self._check_valid_prescription_order_line(rx_lines)

        lines = [
            (
                0,
                0,
                {
                    "prescription_line_id": rxl.id,
                    "product_id": rxl.product_id.id,
                    "date_schedule": rxl.date_schedule,
                    "remaining_uom_qty": rxl.remaining_uom_qty,
                    "price_unit": rxl.price_unit,
                    "product_uom": rxl.product_uom,
                    "qty": rxl.remaining_uom_qty,
                    "partner_id": rxl.partner_id,
                },
            )
            for rxl in rx_lines.filtered(
                lambda rx_line: not rx_line.display_type
                and rx_line.remaining_uom_qty != 0.0
            )
        ]
        return lines

    prescription_order_id = fields.Many2one(
        comodel_name="prescription.order",
        readonly=True,
        default=lambda self: self._default_order(),
    )
    sale_order_id = fields.Many2one(
        "sale.order", string="Purchase Order", domain=[("state", "=", "draft")]
    )
    line_ids = fields.One2many(
        "prescription.order.wizard.line",
        "wizard_id",
        string="Lines",
        default=_default_lines,
    )

    def _prepare_so_line_vals(self, line):
        return {
            "product_id": line.product_id.id,
            "name": line.product_id.name,
            "product_uom": line.product_uom.id,
            "sequence": line.prescription_line_id.sequence,
            "price_unit": line.prescription_line_id.price_unit,
            "prescription_order_line": line.prescription_line_id.id,
            "product_uom_qty": line.qty,
            "tax_id": [(6, 0, line.taxes_id.ids)],
        }

    def _prepare_so_vals(
        self,
        customer,
        user_id,
        currency_id,
        pricelist_id,
        payment_term_id,
        order_lines_by_customer,
    ):
        return {
            "partner_id": customer,
            "origin": self.prescription_order_id.name,
            "user_id": user_id,
            "currency_id": currency_id,
            "pricelist_id": pricelist_id,
            "payment_term_id": payment_term_id,
            "order_line": order_lines_by_customer[customer],
            "analytic_account_id": self.prescription_order_id.analytic_account_id.id,
        }

    def create_sale_order(self):
        order_lines_by_customer = defaultdict(list)
        currency_id = 0
        pricelist_id = 0
        user_id = 0
        payment_term_id = 0
        for line in self.line_ids.filtered(lambda line: line.qty != 0.0):
            if line.qty > line.remaining_uom_qty:
                raise UserError(_("You can't order more than the remaining quantities"))
            vals = self._prepare_so_line_vals(line)
            order_lines_by_customer[line.partner_id.id].append((0, 0, vals))

            if currency_id == 0:
                currency_id = line.prescription_line_id.order_id.currency_id.id
            elif currency_id != line.prescription_line_id.order_id.currency_id.id:
                currency_id = False

            if pricelist_id == 0:
                pricelist_id = line.prescription_line_id.pricelist_id.id
            elif pricelist_id != line.prescription_line_id.pricelist_id.id:
                pricelist_id = False

            if user_id == 0:
                user_id = line.prescription_line_id.user_id.id
            elif user_id != line.prescription_line_id.user_id.id:
                user_id = False

            if payment_term_id == 0:
                payment_term_id = line.prescription_line_id.payment_term_id.id
            elif payment_term_id != line.prescription_line_id.payment_term_id.id:
                payment_term_id = False

        if not order_lines_by_customer:
            raise UserError(_("An order can't be empty"))

        if not currency_id:
            raise UserError(
                _(
                    "Can not create Sale Order from Prescription "
                    "Order lines with different currencies"
                )
            )

        res = []
        for customer in order_lines_by_customer:
            order_vals = self._prepare_so_vals(
                customer,
                user_id,
                currency_id,
                pricelist_id,
                payment_term_id,
                order_lines_by_customer,
            )
            sale_order = self.env["sale.order"].create(order_vals)
            res.append(sale_order.id)
        return {
            "domain": [("id", "in", res)],
            "name": _("Sales Orders"),
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "sale.order",
            "context": {"from_sale_order": True},
            "type": "ir.actions.act_window",
        }


class PrescriptionOrderWizardLine(models.TransientModel):
    _name = "prescription.order.wizard.line"
    _description = "Prescription order wizard line"

    wizard_id = fields.Many2one("prescription.order.wizard")
    prescription_line_id = fields.Many2one("prescription.order.line")
    product_id = fields.Many2one(
        "product.product", related="prescription_line_id.product_id", string="Product"
    )
    product_uom = fields.Many2one(
        "uom.uom", related="prescription_line_id.product_uom", string="Unit of Measure"
    )
    date_schedule = fields.Date(string="Scheduled Date")
    remaining_uom_qty = fields.Float(related="prescription_line_id.remaining_uom_qty")
    qty = fields.Float(string="Quantity to Order", required=True)
    price_unit = fields.Float(related="prescription_line_id.price_unit")
    currency_id = fields.Many2one("res.currency", related="prescription_line_id.currency_id")
    partner_id = fields.Many2one(
        "res.partner", related="prescription_line_id.partner_id", string="Vendor"
    )
    taxes_id = fields.Many2many("account.tax", related="prescription_line_id.taxes_id")
