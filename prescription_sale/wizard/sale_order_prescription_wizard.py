from odoo import SUPERUSER_ID, _, api, fields, models


class SaleOrderPrescriptionWizard(models.TransientModel):
    _name = "sale.order.prescription.wizard"
    _description = "Sale Order Prescription Wizard"

    def _domain_location_id(self):
        sale = self.env["sale.order"].browse(self.env.context.get("active_id"))
        prescription_loc = (
            self.env["stock.warehouse"]
            .search([("company_id", "=", sale.company_id.id)])
            .mapped("prescription_loc_id")
        )
        return [("id", "child_of", prescription_loc.ids)]

    order_id = fields.Many2one(
        comodel_name="sale.order",
        default=lambda self: self.env.context.get("active_id", False),
    )
    line_ids = fields.One2many(
        comodel_name="sale.order.line.prescription.wizard",
        inverse_name="wizard_id",
        string="Lines",
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Prescription location",
        domain=_domain_location_id,
        default=lambda r: r.order_id.warehouse_id.prescription_loc_id.id,
    )
    commercial_partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="order_id.partner_id.commercial_partner_id",
        string="Commercial entity",
    )
    partner_shipping_id = fields.Many2one(
        comodel_name="res.partner",
        string="Shipping Address",
        help="Will be used to return the goods when the Prescription is completed",
    )
    custom_description = fields.Text(
        help="Values coming from portal Prescription request form custom fields",
    )

    def create_prescription(self, from_portal=False):
        self.ensure_one()
        user_has_group_portal = self.env.user.has_group(
            "base.group_portal"
        ) or self.env.user.has_group("base.group_public")
        lines = self.line_ids.filtered(lambda r: r.quantity > 0.0)
        val_list = [line._prepare_prescription_values() for line in lines]
        prescription_model = (
            self.env["prescription"].with_user(SUPERUSER_ID)
            if user_has_group_portal
            else self.env["prescription"]
        )
        prescription = prescription_model.create(val_list)
        if from_portal:
            prescription._add_message_subscribe_partner()
        # post messages
        msg_list = [
            '<a href="#" data-oe-model="prescription" data-oe-id="%d">%s</a>' % (r.id, r.name)
            for r in prescription
        ]
        msg = ", ".join(msg_list)
        if len(msg_list) == 1:
            self.order_id.message_post(body=_(msg + " has been created."))
        elif len(msg_list) > 1:
            self.order_id.message_post(body=_(msg + " have been created."))
        prescription.message_post_with_view(
            "mail.message_origin_link",
            values={"self": prescription, "origin": self.order_id},
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        return prescription

    def create_and_open_prescription(self):
        self.ensure_one()
        prescription = self.create_prescription()
        if not prescription:
            return
        for rec in prescription:
            rec.action_confirm()
        action = self.sudo().env.ref("prescription.prescription_action").read()[0]
        if len(prescription) > 1:
            action["domain"] = [("id", "in", prescription.ids)]
        elif prescription:
            action.update(
                res_id=prescription.id,
                view_mode="form",
                view_id=False,
                views=False,
            )
        return action


class SaleOrderLinePrescriptionWizard(models.TransientModel):
    _name = "sale.order.line.prescription.wizard"
    _description = "Sale Order Line Prescription Wizard"

    wizard_id = fields.Many2one(comodel_name="sale.order.prescription.wizard", string="Wizard")
    order_id = fields.Many2one(
        comodel_name="sale.order",
        default=lambda self: self.env["sale.order"].browse(
            self.env.context.get("active_id", False)
        ),
    )
    allowed_product_ids = fields.Many2many(
        comodel_name="product.product", compute="_compute_allowed_product_ids"
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        domain="[('id', 'in', allowed_product_ids)]",
    )
    uom_category_id = fields.Many2one(
        comodel_name="uom.category",
        related="product_id.uom_id.category_id",
    )
    quantity = fields.Float(
        digits="Product Unit of Measure",
        required=True,
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', uom_category_id)]",
        required=True,
    )
    allowed_picking_ids = fields.Many2many(
        comodel_name="stock.picking", compute="_compute_allowed_picking_ids"
    )
    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Delivery order",
        domain="[('id', 'in', allowed_picking_ids)]",
    )
    move_id = fields.Many2one(comodel_name="stock.move", compute="_compute_move_id")
    operation_id = fields.Many2one(
        comodel_name="prescription.operation",
        string="Requested operation",
    )
    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
    )
    description = fields.Text()

    @api.onchange("product_id")
    def onchange_product_id(self):
        self.picking_id = False
        self.uom_id = self.product_id.uom_id

    @api.depends("picking_id")
    def _compute_move_id(self):
        for record in self:
            move_id = False
            if record.picking_id:
                move_id = record.picking_id.move_ids.filtered(
                    lambda r: (
                        r.sale_line_id == record.sale_line_id
                        and r.sale_line_id.product_id == record.product_id
                        and r.sale_line_id.order_id == record.order_id
                        and r.state == "done"
                    )
                )
            record.move_id = move_id

    @api.depends("order_id")
    def _compute_allowed_product_ids(self):
        for record in self:
            product_ids = record.order_id.order_line.mapped("product_id.id")
            record.allowed_product_ids = product_ids

    @api.depends("product_id")
    def _compute_allowed_picking_ids(self):
        for record in self:
            line = record.order_id.order_line.filtered(
                lambda r: r.product_id == record.product_id
            )
            record.allowed_picking_ids = line.mapped("move_ids.picking_id").filtered(
                lambda x: x.state == "done"
            )

    def _prepare_prescription_values(self):
        self.ensure_one()
        partner_shipping = (
            self.wizard_id.partner_shipping_id or self.order_id.partner_shipping_id
        )
        description = (self.description or "") + (
            self.wizard_id.custom_description or ""
        )
        return {
            "partner_id": self.order_id.partner_id.id,
            "partner_invoice_id": self.order_id.partner_invoice_id.id,
            "partner_shipping_id": partner_shipping.id,
            "origin": self.order_id.name,
            "company_id": self.order_id.company_id.id,
            "location_id": self.wizard_id.location_id.id,
            "order_id": self.order_id.id,
            "picking_id": self.picking_id.id,
            "move_id": self.move_id.id,
            "product_id": self.product_id.id,
            "product_uom_qty": self.quantity,
            "product_uom": self.uom_id.id,
            "operation_id": self.operation_id.id,
            "description": description,
        }
