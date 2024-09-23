from odoo import SUPERUSER_ID, Command, fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date


class PrescriptionOrder(models.Model):
    _name = "prescription.order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Prescription Order"
    _check_company_auto = True

    @api.model
    def _default_note(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account.use_invoice_terms")
            and self.env.company.invoice_terms
            or ""
        )

    @api.depends("line_ids.price_total")
    def _compute_amount_all(self):
        for order in self.filtered("currency_id"):
            amount_untaxed = amount_tax = 0.0
            for line in order.line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update(
                {
                    "amount_untaxed": order.currency_id.round(amount_untaxed),
                    "amount_tax": order.currency_id.round(amount_tax),
                    "amount_total": amount_untaxed + amount_tax,
                }
            )

    name = fields.Char(default="Draft", readonly=True, copy=False)
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
    )
    practitioner_id = fields.Many2one(
        string='Practitioner',
        comodel_name='res.partner',
        domain="[('is_practitioner', '=', True)]",
        required=True,
        track_visibility='onchange'
    )
    patient_id = fields.Many2one(
        string='Patient',
        comodel_name='res.partner',
        domain="[('is_patient', '=', True)]",
        required=True,
        track_visibility='onchange'
    )
    location_id = fields.Many2one(
        string='Location',
        comodel_name='res.partner',
        domain="[('is_location', '=', True)]",
        required=True,
        track_visibility='onchange'
    )
    user_id = fields.Many2one(
        "res.users",
        string="Salesperson",
    )
    team_id = fields.Many2one(
        "crm.team",
        string="Sales Team",
        change_default=True,
        default=lambda self: self.env["crm.team"]._get_default_team_id(),
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )

    pos_order_uid = fields.Char(help="Related Pos order", string='Related Pos order')
    client_order_ref = fields.Char(string="Customer Reference",copy=False)
    line_ids = fields.One2many(
        "prescription.order.line", "order_id", string="Order lines", copy=True
    )
    line_count = fields.Integer(
        string="Prescription Order Line count",
        compute="_compute_line_count",
        readonly=True,
    )
    product_id = fields.Many2one(
        "product.product",
        related="line_ids.product_id",
        string="Product",
    )
    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist",
        required=True,
    )
    currency_id = fields.Many2one("res.currency", related="pricelist_id.currency_id")
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        copy=False,
        check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    payment_term_id = fields.Many2one(
        "account.payment.term",
        string="Payment Terms",
    )
    confirmed = fields.Boolean(copy=False)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("open", "Open"),
            ("done", "Done"),
            ("expired", "Expired"),
        ],
        compute="_compute_state",
        store=True,
        copy=False,
    )
    book_in_date = fields.Datetime(string='Book In')
    book_out_date = fields.Datetime(string='Book Out')
    draft_date = fields.Datetime(string='Draft/Quote Date', help="Draft/Quotation created date", readonly=True, index=True, default=fields.Datetime.now)
    order_date = fields.Date(string='Order Date', help="Order created date", readonly=True, index=True, default=fields.Date.today())
    delivered_date = fields.Datetime(string='Delivered Date', readonly=True, help="Delivering date of the order")
    validity_date = fields.Date()
    note = fields.Text(default=_default_note)
    sale_count = fields.Integer(compute="_compute_sale_count")
    fiscal_position_id = fields.Many2one("account.fiscal.position", string="Fiscal Position")
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        store=True,
        readonly=True,
        compute="_compute_amount_all",
        tracking=True,
    )
    amount_tax = fields.Monetary(
        string="Taxes", store=True, readonly=True, compute="_compute_amount_all"
    )
    amount_total = fields.Monetary(
        string="Total", store=True, readonly=True, compute="_compute_amount_all"
    )

    # Fields use to filter in tree view
    original_uom_qty = fields.Float(
        string="Original quantity",
        compute="_compute_uom_qty",
        search="_search_original_uom_qty",
        default=0.0,
    )
    ordered_uom_qty = fields.Float(
        string="Ordered quantity",
        compute="_compute_uom_qty",
        search="_search_ordered_uom_qty",
        default=0.0,
    )
    invoiced_uom_qty = fields.Float(
        string="Invoiced quantity",
        compute="_compute_uom_qty",
        search="_search_invoiced_uom_qty",
        default=0.0,
    )
    remaining_uom_qty = fields.Float(
        string="Remaining quantity",
        compute="_compute_uom_qty",
        search="_search_remaining_uom_qty",
        default=0.0,
    )
    delivered_uom_qty = fields.Float(
        string="Delivered quantity",
        compute="_compute_uom_qty",
        search="_search_delivered_uom_qty",
        default=0.0,
    )

    def _get_sale_orders(self):
        return self.mapped("line_ids.sale_lines.order_id")

    @api.depends("line_ids")
    def _compute_line_count(self):
        self.line_count = len(self.mapped("line_ids"))

    def _compute_sale_count(self):
        for prescription_order in self:
            prescription_order.sale_count = len(prescription_order._get_sale_orders())

    @api.depends(
        "line_ids.remaining_uom_qty",
        "validity_date",
        "confirmed",
    )
    def _compute_state(self):
        today = fields.Date.today()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for order in self:
            if not order.confirmed:
                order.state = "draft"
            elif order.validity_date <= today:
                order.state = "expired"
            elif float_is_zero(
                sum(
                    order.line_ids.filtered(lambda line: not line.display_type).mapped(
                        "remaining_uom_qty"
                    )
                ),
                precision_digits=precision,
            ):
                order.state = "done"
            else:
                order.state = "open"

    def _compute_uom_qty(self):
        for rx in self:
            rx.original_uom_qty = sum(rx.mapped("line_ids.original_uom_qty"))
            rx.ordered_uom_qty = sum(rx.mapped("line_ids.ordered_uom_qty"))
            rx.invoiced_uom_qty = sum(rx.mapped("line_ids.invoiced_uom_qty"))
            rx.delivered_uom_qty = sum(rx.mapped("line_ids.delivered_uom_qty"))
            rx.remaining_uom_qty = sum(rx.mapped("line_ids.remaining_uom_qty"))

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment term
        - Fiscal position
        """
        if not self.partner_id:
            self.payment_term_id = False
            self.fiscal_position_id = False
            return

        values = {
            "pricelist_id": (
                self.partner_id.property_product_pricelist
                and self.partner_id.property_product_pricelist.id
                or False
            ),
            "payment_term_id": (
                self.partner_id.property_payment_term_id
                and self.partner_id.property_payment_term_id.id
                or False
            ),
            "fiscal_position_id": self.env["account.fiscal.position"]
            .with_context(company_id=self.company_id.id)
            ._get_fiscal_position(self.partner_id),
        }

        if self.partner_id.user_id:
            values["user_id"] = self.partner_id.user_id.id
        if self.partner_id.team_id:
            values["team_id"] = self.partner_id.team_id.id
        self.update(values)

    # def action_config_start(self):
    #     """Return action to start configuration wizard"""
    #     configurator_obj = self.env["product.configurator.prescription.order"]
    #     ctx = dict(
    #         self.env.context,
    #         default_order_id=self.id,
    #         wizard_model="product.configurator.prescription.order",
    #         allow_preset_selection=True,
    #     )
    #     return configurator_obj.with_context(**ctx).get_wizard_action()


    @api.model
    def create(self, vals):
        """Inherited create function to generate sequence number for prescription orders."""
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('prescription.order') or '/'
        if not vals.get('team_id'):
            raise ValidationError("The Team field must be set when creating a prescription order.")
        return super(PrescriptionOrder, self).create(vals)

    @api.model
    def create_prescription_order(self, partner, phone, address, date, price_list, product, note, delivered_date, pos_order, team_id):
        """Creates a prescription order based on the values in the prescription popup in PoS UI."""
        order = self.create({
            'partner_id': partner,
            'phone': phone,
            'delivery_address': address,
            'pricelist_id': price_list if price_list else False,
            'draft_date': fields.Date.today(),
            'pos_order_uid': pos_order,
            'team': team_id,
            'prescription_line_ids': [Command.create({
                'product_id': product['product_id'][i],
                'qty': product['qty'][i],
                'price_unit': product['price'][i],
            }) for i in range(len(product['product_id']))],
            'note': note,
        })

        if delivered_date:
            order.write({'delivered_date': delivered_date + ' 00:00:00'})
        return order.name

    @api.model
    def all_orders(self):
        """Fetches all draft stage orders to PoS Prescription orders screen."""
        values = []
        for rec in self.search([('state', '=', 'draft')]):
            products = []
            for line in rec.prescription_line_ids:
                products.append({
                    'id': line.product_id.id,
                    'qty': line.qty,
                    'price': line.price_unit
                })
            values.append({
                'id': rec.id,
                'name': rec.name,
                'partner_id': rec.partner_id.id,
                'partner_name': rec.partner_id.name,
                'address': rec.delivery_address,
                'note': rec.note,
                'phone': rec.phone,
                'date': rec.draft_date,
                'deliver': rec.delivered_date,
                'products': products,
                'total': rec.amount_total
            })
        return values

    def unlink(self):
        for order in self:
            if order.state not in ("draft", "expired") or order._check_active_orders():
                raise UserError(
                    _(
                        "You can not delete an open prescription or "
                        "with active sale orders! "
                        "Try to cancel it before."
                    )
                )
        return super().unlink()

    def _validate(self):
        try:
            today = fields.Date.today()
            for order in self:
                assert order.validity_date, _("Validity date is mandatory")
                assert order.validity_date > today, _(
                    "Validity date must be in the future"
                )
                assert order.partner_id, _("Partner is mandatory")
                assert len(order.line_ids) > 0, _("Must have some lines")
                order.line_ids._validate()
        except AssertionError as e:
            raise UserError(e) from e

    def set_to_draft(self):
        for order in self:
            order.write({"state": "draft", "confirmed": False})
        return True

    def action_confirm(self):
        self._validate()
        for order in self:
            sequence_obj = self.env["ir.sequence"]
            if order.company_id:
                sequence_obj = sequence_obj.with_company(order.company_id.id)
            name = sequence_obj.next_by_code("prescription.order")
            order.write({"confirmed": True, "name": name})
        return True

    def _check_active_orders(self):
        for order in self.filtered("sale_count"):
            for so in order._get_sale_orders():
                if so.state not in ("cancel"):
                    return True
        return False

    def action_cancel(self):
        for order in self:
            if order._check_active_orders():
                raise UserError(
                    _(
                        "You can not delete a prescription order with opened "
                        "sale orders! "
                        "Try to cancel them before."
                    )
                )
            order.write({"state": "expired"})
        return True

    def action_view_sale_orders(self):
        sale_orders = self._get_sale_orders()
        action = self.env["ir.actions.act_window"]._for_xml_id("sale.action_orders")
        if len(sale_orders) > 0:
            action["domain"] = [("id", "in", sale_orders.ids)]
            action["context"] = [("id", "in", sale_orders.ids)]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def action_view_prescription_order_line(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "nwpl_pod_master.act_open_prescription_order_lines_view_tree"
        )
        lines = self.mapped("line_ids")
        if len(lines) > 0:
            action["domain"] = [("id", "in", lines.ids)]
        return action

    @api.model
    def expire_orders(self):
        today = fields.Date.today()
        expired_orders = self.search(
            [("state", "=", "open"), ("validity_date", "<=", today)]
        )
        expired_orders.modified(["validity_date"])
        expired_orders.flush_recordset()

    @api.model
    def _search_original_uom_qty(self, operator, value):
        rx_line_obj = self.env["prescription.order.line"]
        res = []
        rx_lines = rx_line_obj.search([("original_uom_qty", operator, value)])
        order_ids = rx_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_ordered_uom_qty(self, operator, value):
        rx_line_obj = self.env["prescription.order.line"]
        res = []
        rx_lines = rx_line_obj.search([("ordered_uom_qty", operator, value)])
        order_ids = rx_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_invoiced_uom_qty(self, operator, value):
        rx_line_obj = self.env["prescription.order.line"]
        res = []
        rx_lines = rx_line_obj.search([("invoiced_uom_qty", operator, value)])
        order_ids = rx_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_delivered_uom_qty(self, operator, value):
        rx_line_obj = self.env["prescription.order.line"]
        res = []
        rx_lines = rx_line_obj.search([("delivered_uom_qty", operator, value)])
        order_ids = rx_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_remaining_uom_qty(self, operator, value):
        rx_line_obj = self.env["prescription.order.line"]
        res = []
        rx_lines = rx_line_obj.search([("remaining_uom_qty", operator, value)])
        order_ids = rx_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

