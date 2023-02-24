# See LICENSE file for full copyright and licensing details.
import time
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import get_lang


class PrescriptionDeviceLine(models.Model):

    _name = "prescription.device.line"
    _description = "Podiatry Device Reservation"
    _rec_name = "device_id"

    device_id = fields.Many2one("podiatry.device", ondelete="restrict", index=True)
    book_in = fields.Datetime("Book In Date", required=True)
    book_out = fields.Datetime("Book Out Date", required=True)
    prescription_id = fields.Many2one("podiatry.prescription", "Prescription Number", ondelete="cascade")
    status = fields.Selection(related="prescription_id.state", string="state")


class PodiatryPrescription(models.Model):

    _name = "podiatry.prescription"
    _description = "podiatry prescription"
    _rec_name = "order_id"

    def name_get(self):
        res = []
        fname = ""
        for rec in self:
            if rec.order_id:
                fname = str(rec.name)
                res.append((rec.id, fname))
        return res

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if args is None:
            args = []
        args += [("name", operator, name)]
        prescription = self.search(args, limit=100)
        return prescription.name_get()

    @api.model
    def _get_bookin_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        bookin_date = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        return fields.Datetime.to_string(bookin_date)

    @api.model
    def _get_bookout_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        bookout_date = fields.Datetime.context_timestamp(
            self, fields.Datetime.now() + timedelta(days=1)
        )
        return fields.Datetime.to_string(bookout_date)

    name = fields.Char("Prescription Number", readonly=True, index=True, default="New")
    order_id = fields.Many2one(
        "sale.order", "Order", delegate=True, required=True, ondelete="cascade"
    )
    bookin_date = fields.Datetime(
        "Book In",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_get_bookin_date,
    )
    bookout_date = fields.Datetime(
        "Book Out",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_get_bookout_date,
    )
    device_line_ids = fields.One2many(
        "podiatry.prescription.line",
        "prescription_id",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        help="Podiatry device reservation detail.",
    )
    accommodation_line_ids = fields.One2many(
        "podiatry.accommodation.line",
        "prescription_id",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        help="Podiatry accommodations details provided to"
        "Customer and it will included in "
        "the main Invoice.",
    )
    podiatry_policy = fields.Selection(
        [
            ("prepaid", "On Booking"),
            ("manual", "On Book In"),
            ("picking", "On Bookout"),
        ],
        default="manual",
        help="Podiatry policy for payment that "
        "either the guest has to payment at "
        "booking time or check-in "
        "check-out time.",
    )
    quantity = fields.Float(
        "Quantity in Days",
        help="Number of days which will automatically "
        "count from the check-in and check-out date. ",
    )
    podiatry_invoice_id = fields.Many2one("account.move", "Invoice", copy=False)
    quantity_dummy = fields.Float()

    @api.constrains("device_line_ids")
    def _check_duplicate_prescription_device_line(self):
        """
        This method is used to validate the device_lines.
        ------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        for rec in self:
            for product in rec.device_line_ids.mapped("product_id"):
                for line in rec.device_line_ids.filtered(
                    lambda l: l.product_id == product
                ):
                    record = rec.device_line_ids.search(
                        [
                            ("product_id", "=", product.id),
                            ("prescription_id", "=", rec.id),
                            ("id", "!=", line.id),
                            # ("bookin_date", ">=", line.bookin_date),
                            # ("bookout_date", "<=", line.bookout_date),
                        ]
                    )
                    if record:
                        raise ValidationError(
                            _(
                                """Device Duplicate Exceeded!, """
                                """You Cannot Take Same %s Device Twice!"""
                            )
                            % (product.name)
                        )

    def _update_prescription_line(self, prescription_id):
        prescription_device_line_obj = self.env["prescription.device.line"]
        podiatry_device_obj = self.env["podiatry.device"]
        for rec in prescription_id:
            for device_rec in rec.device_line_ids:
                device = podiatry_device_obj.search(
                    [("product_id", "=", device_rec.product_id.id)]
                )
                device.write({"isdevice": False})
                vals = {
                    "device_id": device.id,
                    # "book_in": rec.bookin_date,
                    # "book_out": rec.bookout_date,
                    "prescription_id": rec.id,
                }
                prescription_device_line_obj.create(vals)

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for podiatry prescription.
        """
        if not "accommodation_line_ids" and "prescription_id" in vals:
            tmp_device_lines = vals.get("device_line_ids", [])
            vals["order_policy"] = vals.get("podiatry_policy", "manual")
            vals.update({"device_line_ids": []})
            prescription_id = super(PodiatryPrescription, self).create(vals)
            for line in tmp_device_lines:
                line[2].update({"prescription_id": prescription_id.id})
            vals.update({"device_line_ids": tmp_device_lines})
            prescription_id.write(vals)
        else:
            if not vals:
                vals = {}
            vals["name"] = self.env["ir.sequence"].next_by_code("podiatry.prescription")
            vals["quantity"] = vals.get("quantity", 0.0) or vals.get("quantity", 0.0)
            prescription_id = super(PodiatryPrescription, self).create(vals)
            self._update_prescription_line(prescription_id)
        return prescription_id

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        product_obj = self.env["product.product"]
        podiatry_device_obj = self.env["podiatry.device"]
        prescription_device_line_obj = self.env["prescription.device.line"]
        for rec in self:
            devices_list = [res.product_id.id for res in rec.device_line_ids]
            if vals and vals.get("quantity", False):
                vals["quantity"] = vals.get("quantity", 0.0)
            else:
                vals["quantity"] = rec.quantity
            device_lst = [prescription_rec.product_id.id for prescription_rec in rec.device_line_ids]
            new_devices = set(device_lst).difference(set(devices_list))
            if len(list(new_devices)) != 0:
                device_list = product_obj.browse(list(new_devices))
                for device in device_list:
                    device_obj = podiatry_device_obj.search([("product_id", "=", device.id)])
                    device_obj.write({"isdevice": False})
                    vals = {
                        "device_id": device_obj.id,
                        # "book_in": rec.bookin_date,
                        # "book_out": rec.bookout_date,
                        "prescription_id": rec.id,
                    }
                    prescription_device_line_obj.create(vals)
            if not len(list(new_devices)):
                device_list_obj = product_obj.browse(devices_list)
                for device in device_list_obj:
                    device_obj = podiatry_device_obj.search([("product_id", "=", device.id)])
                    device_obj.write({"isdevice": False})
                    device_vals = {
                        "device_id": device_obj.id,
                        # "book_in": rec.bookin_date,
                        # "book_out": rec.bookout_date,
                        "prescription_id": rec.id,
                    }
                    prescription_device_line_rec = prescription_device_line_obj.search(
                        [("prescription_id", "=", rec.id)]
                    )
                    prescription_device_line_rec.write(device_vals)
        return super(PodiatryPrescription, self).write(vals)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        """
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the podiatry prescription as well
        ---------------------------------------------------------------
        @param self: object pointer
        """
        if self.partner_id:
            self.update(
                {
                    "partner_invoice_id": self.partner_id.id,
                    "partner_shipping_id": self.partner_id.id,
                    "pricelist_id": self.partner_id.property_product_pricelist.id,
                }
            )

    def action_done(self):
        self.write({"state": "done"})

    def action_cancel(self):
        """
        @param self: object pointer
        """
        for rec in self:
            if not rec.order_id:
                raise UserError(_("Order id is not available"))
            for product in rec.device_line_ids.filtered(
                lambda l: l.order_line_id.product_id == product
            ):
                devices = self.env["podiatry.device"].search([("product_id", "=", product.id)])
                devices.write({"isdevice": True, "status": "available"})
            rec.invoice_ids.button_cancel()
            return rec.order_id.action_cancel()

    def action_confirm(self):
        for order in self.order_id:
            order.state = "sale"
            if not order.analytic_account_id:
                if order.order_line.filtered(
                    lambda line: line.product_id.invoice_policy == "cost"
                ):
                    order._create_analytic_account()
            config_parameter_obj = self.env["ir.config_parameter"]
            if config_parameter_obj.sudo().get_param("sale.auto_done_setting"):
                self.order_id.action_done()

    def action_cancel_draft(self):
        """
        @param self: object pointer
        """
        order_line_recs = self.env["sale.order.line"].search(
            [("order_id", "in", self.ids), ("state", "=", "cancel")]
        )
        self.write({"state": "draft", "invoice_ids": []})
        order_line_recs.write(
            {
                "invoiced": False,
                "state": "draft",
                "invoice_lines": [(6, 0, [])],
            }
        )


class PodiatryPrescriptionLine(models.Model):

    _name = "podiatry.prescription.line"
    _description = "Podiatry Prescription Line"

    order_line_id = fields.Many2one(
        "sale.order.line",
        "Order Line",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    prescription_id = fields.Many2one("podiatry.prescription", "Prescription", ondelete="cascade")
    # bookin_date = fields.Datetime("Book In", required=True)
    # bookout_date = fields.Datetime("Book Out", required=True)
    is_reserved = fields.Boolean(help="True when prescription line created from Reservation")

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for podiatry prescription line.
        """
        if "prescription_id" in vals:
            prescription = self.env["podiatry.prescription"].browse(vals["prescription_id"])
            vals.update({"order_id": prescription.order_id.id})
        return super(PodiatryPrescriptionLine, self).create(vals)

    # @api.constrains("bookin_date", "bookout_date")
    # def _check_dates(self):
    #     """
    #     This method is used to validate the bookin_date and bookout_date.
    #     -------------------------------------------------------------------
    #     @param self: object pointer
    #     @return: raise warning depending on the validation
    #     """
    #     if self.bookin_date >= self.bookout_date:
    #         raise ValidationError(
    #             _(
    #                 """Device line Book In Date Should be """
    #                 """less than the Book Out Date!"""
    #             )
    #         )
    #     if self.prescription_id.date_order and self.bookin_date:
    #         if self.bookin_date.date() < self.prescription_id.date_order.date():
    #             raise ValidationError(
    #                 _(
    #                     """Device line check in date should be """
    #                     """greater than the current date."""
    #                 )
    #             )

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        for line in self:
            if line.order_line_id:
                devices = self.env["podiatry.device"].search(
                    [("product_id", "=", line.order_line_id.product_id.id)]
                )
                prescription_device_lines = self.env["prescription.device.line"].search(
                    [
                        ("prescription_id", "=", line.prescription_id.id),
                        ("device_id", "in", devices.ids),
                    ]
                )
                prescription_device_lines.unlink()
                devices.write({"isdevice": True, "status": "available"})
                line.order_line_id.unlink()
        return super(PodiatryPrescriptionLine, self).unlink()

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
        :param obj product: object of current product record
        :parem float qty: total quentity of product
        :param tuple price_and_rule: tuple(price, suitable_rule) coming
        from pricelist computation
        :param obj uom: unit of measure of current order line
        :param integer pricelist_id: pricelist id of sale order"""
        PricelistItem = self.env["product.pricelist.item"]
        field_name = "lst_price"
        currency_id = None
        product_currency = None
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == "without_discount":
                while (
                    pricelist_item.base == "pricelist"
                    and pricelist_item.base_pricelist_id
                    and pricelist_item.base_pricelist_id.discount_policy
                    == "without_discount"
                ):
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(
                        uom=uom.id
                    ).get_product_price_rule(product, qty, self.prescription_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == "standard_price":
                field_name = "standard_price"
            if pricelist_item.base == "pricelist" and pricelist_item.base_pricelist_id:
                field_name = "price"
                product = product.with_context(
                    pricelist=pricelist_item.base_pricelist_id.id
                )
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        product_currency = (
            product_currency
            or (product.company_id and product.company_id.currency_id)
            or self.env.user.company_id.currency_id
        )
        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(
                    product_currency, currency_id
                )

        product_uom = self.env.context.get("uom") or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0
        return product[field_name] * uom_factor * cur_factor, currency_id.id

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        if self.prescription_id.pricelist_id.discount_policy == "with_discount":
            return product.with_context(pricelist=self.prescription_id.pricelist_id.id).price
        product_context = dict(
            self.env.context,
            partner_id=self.prescription_id.partner_id.id,
            date=self.prescription_id.date_order,
            uom=self.product_uom.id,
        )
        final_price, rule_id = self.prescription_id.pricelist_id.with_context(
            **product_context
        ).get_product_price_rule(
            self.product_id,
            self.product_uom_qty or 1.0,
            self.prescription_id.partner_id,
        )
        base_price, currency_id = self.with_context(
            **product_context
        )._get_real_price_currency(
            product,
            rule_id,
            self.product_uom_qty,
            self.product_uom,
            self.prescription_id.pricelist_id.id,
        )
        if currency_id != self.prescription_id.pricelist_id.currency_id.id:
            base_price = (
                self.env["res.currency"]
                .browse(currency_id)
                .with_context(**product_context)
                .compute(base_price, self.prescription_id.pricelist_id.currency_id)
            )
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = (
                line.order_id.fiscal_position_id
                or line.order_id.fiscal_position_id.get_fiscal_position(
                    line.order_partner_id.id
                )
            )
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(
                lambda t: t.company_id == line.env.company
            )
            line.tax_id = fpos.map_tax(taxes)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if not self.product_id:
            return
        product_tmpl = self.product_id.product_tmpl_id
        attribute_lines = product_tmpl.valid_product_template_attribute_line_ids
        valid_values = attribute_lines.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals["product_uom"] = self.product_id.uom_id
            vals["product_uom_qty"] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get("product_uom_qty") or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
        )

        vals.update(
            name=self.order_line_id.get_sale_order_line_multiline_description_sale(
                product
            )
        )

        self._compute_tax_id()

        if self.prescription_id.pricelist_id and self.prescription_id.partner_id:
            vals["price_unit"] = self.env[
                "account.tax"
            ]._fix_tax_included_price_company(
                self._get_display_price(product),
                product.taxes_id,
                self.tax_id,
                self.company_id,
            )
        self.update(vals)

        title = False
        message = False
        result = {}
        warning = {}
        if product.sale_line_warn != "no-message":
            title = _("Warning for %s", product.name)
            message = product.sale_line_warn_msg
            warning["title"] = title
            warning["message"] = message
            result = {"warning": warning}
            if product.sale_line_warn == "block":
                self.product_id = False
        return result

    # @api.onchange("bookin_date", "bookout_date")
    # def _onchange_bookin_bookout_dates(self):
    #     """
    #     When you change bookin_date or bookout_date it will checked it
    #     and update the qty of podiatry prescription line
    #     -----------------------------------------------------------------
    #     @param self: object pointer
    #     """

    #     configured_addition_hours = (
    #         self.prescription_id.warehouse_id.company_id.additional_hours
    #     )
    #     myquantity = 0
    #     if self.bookin_date and self.bookout_date:
    #         qty = self.bookout_date - self.bookin_date
    #         sec_qty = qty.seconds
    #         if (not qty.days and not sec_qty) or (qty.days and not sec_qty):
    #             myquantity = qty.days
    #         else:
    #             myquantity = qty.days + 1
    #         if configured_addition_hours > 0:
    #             additional_hours = abs((qty.seconds / 60) / 60)
    #             if additional_hours >= configured_addition_hours:
    #                 myquantity += 1
    #     self.product_uom_qty = myquantity

    def copy_data(self, default=None):
        """
        @param self: object pointer
        @param default: dict of default values to be set
        """

        sale_line_obj = self.order_line_id
        return sale_line_obj.copy_data(default=default)


class PodiatryAccommodationLine(models.Model):

    _name = "podiatry.accommodation.line"
    _description = "podiatry Accommodation line"

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        """
        @param self: object pointer
        @param default: dict of default values to be set
        """
        return super(PodiatryAccommodationLine, self).copy(default=default)

    accommodation_line_id = fields.Many2one(
        "sale.order.line",
        "Accommodation Line",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    prescription_id = fields.Many2one("podiatry.prescription", "Prescription", ondelete="cascade")
    # accom_bookin_date = fields.Datetime("From Date")
    # accom_bookout_date = fields.Datetime("To Date")

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for podiatry accommodation line.
        """
        if "prescription_id" in vals:
            prescription = self.env["podiatry.prescription"].browse(vals["prescription_id"])
            vals.update({"order_id": prescription.order_id.id})
        return super(PodiatryAccommodationLine, self).create(vals)

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        self.mapped("accommodation_line_id").unlink()
        return super().unlink()

    def _compute_tax_id(self):
        for line in self:
            fpos = (
                line.prescription_id.fiscal_position_id
                or line.prescription_id.partner_id.property_account_position_id
            )
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(
                lambda r: not line.company_id or r.company_id == line.company_id
            )
            line.tax_id = (
                fpos.map_tax(taxes, line.product_id, line.prescription_id.partner_shipping_id)
                if fpos
                else taxes
            )

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
        :param obj product: object of current product record
        :parem float qty: total quentity of product
        :param tuple price_and_rule: tuple(price, suitable_rule)
        coming from pricelist computation
        :param obj uom: unit of measure of current order line
        :param integer pricelist_id: pricelist id of sale order"""
        PricelistItem = self.env["product.pricelist.item"]
        field_name = "lst_price"
        currency_id = None
        product_currency = None
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == "without_discount":
                while (
                    pricelist_item.base == "pricelist"
                    and pricelist_item.base_pricelist_id
                    and pricelist_item.base_pricelist_id.discount_policy
                    == "without_discount"
                ):
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(
                        uom=uom.id
                    ).get_product_price_rule(product, qty, self.prescription_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == "standard_price":
                field_name = "standard_price"
            if pricelist_item.base == "pricelist" and pricelist_item.base_pricelist_id:
                field_name = "price"
                product = product.with_context(
                    pricelist=pricelist_item.base_pricelist_id.id
                )
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        product_currency = (
            product_currency
            or (product.company_id and product.company_id.currency_id)
            or self.env.user.company_id.currency_id
        )
        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(
                    product_currency, currency_id
                )

        product_uom = self.env.context.get("uom") or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0
        return product[field_name] * uom_factor * cur_factor, currency_id.id

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        if self.prescription_id.pricelist_id.discount_policy == "with_discount":
            return product.with_context(pricelist=self.prescription_id.pricelist_id.id).price
        product_context = dict(
            self.env.context,
            partner_id=self.prescription_id.partner_id.id,
            date=self.prescription_id.date_order,
            uom=self.product_uom.id,
        )
        final_price, rule_id = self.prescription_id.pricelist_id.with_context(
            **product_context
        ).get_product_price_rule(
            self.product_id,
            self.product_uom_qty or 1.0,
            self.prescription_id.partner_id,
        )
        base_price, currency_id = self.with_context(
            **product_context
        )._get_real_price_currency(
            product,
            rule_id,
            self.product_uom_qty,
            self.product_uom,
            self.prescription_id.pricelist_id.id,
        )
        if currency_id != self.prescription_id.pricelist_id.currency_id.id:
            base_price = (
                self.env["res.currency"]
                .browse(currency_id)
                .with_context(**product_context)
                .compute(base_price, self.prescription_id.pricelist_id.currency_id)
            )
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if not self.product_id:
            return
        product_tmpl = self.product_id.product_tmpl_id
        attribute_lines = product_tmpl.valid_product_template_attribute_line_ids
        valid_values = attribute_lines.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals["product_uom"] = self.product_id.uom_id
            vals["product_uom_qty"] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get("product_uom_qty") or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
        )

        vals.update(
            name=self.accommodation_line_id.get_sale_order_line_multiline_description_sale(
                product
            )
        )

        self._compute_tax_id()

        if self.prescription_id.pricelist_id and self.prescription_id.partner_id:
            vals["price_unit"] = self.env[
                "account.tax"
            ]._fix_tax_included_price_company(
                self._get_display_price(product),
                product.taxes_id,
                self.tax_id,
                self.company_id,
            )
        self.update(vals)

        title = False
        message = False
        result = {}
        warning = {}
        if product.sale_line_warn != "no-message":
            title = _("Warning for %s", product.name)
            message = product.sale_line_warn_msg
            warning["title"] = title
            warning["message"] = message
            result = {"warning": warning}
            if product.sale_line_warn == "block":
                self.product_id = False
        return result

    # @api.onchange("accom_bookin_date", "accom_bookout_date")
    # def _on_change_bookin_bookout_dates(self):
    #     """
    #     When you change bookin_date or bookout_date it will checked it
    #     and update the qty of podiatry accommodation line
    #     -----------------------------------------------------------------
    #     @param self: object pointer
    #     """
    #     if not self.accom_bookin_date:
    #         time_a = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    #         self.accom_bookin_date = time_a
    #     if not self.accom_bookout_date:
    #         self.accom_bookout_date = time_a
    #     if self.accom_bookout_date < self.accom_bookin_date:
    #         raise ValidationError(_("Bookout must be greater or equal bookin date"))
    #     if self.accom_bookin_date and self.accom_bookout_date:
    #         diffDate = self.accom_bookout_date - self.accom_bookin_date
    #         qty = diffDate.days + 1
    #         self.product_uom_qty = qty

    def copy_data(self, default=None):
        """
        @param self: object pointer
        @param default: dict of default values to be set
        """
        return self.accommodation_line_id.copy_data(default=default)
