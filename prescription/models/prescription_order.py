# See LICENSE file for full copyright and licensing details.
import time
from datetime import timedelta
from collections import defaultdict
from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round, format_date, groupby
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import get_lang


class OrderDeviceLine(models.Model):

    _name = "order.device.line"
    _description = "Prescription Device Reservation"
    _rec_name = "device_id"

    device_id = fields.Many2one("prescription.device", ondelete="restrict", index=True)
    book_in = fields.Datetime("Book In Date", required=True)
    book_out = fields.Datetime("Book Out Date")
    prescription_order_id = fields.Many2one("prescription.order", "Order Number", ondelete="cascade")
    status = fields.Selection(related="prescription_order_id.state", string="state")


class PrescriptionOrder(models.Model):

    _name = "prescription.order"
    _description = "prescription order"
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

    name = fields.Char("Order Number", readonly=True, index=True, default="New")
    
    order_id = fields.Many2one("sale.order", "Order", delegate=True, required=True, ondelete="cascade")
    
    bookin_date = fields.Datetime(
        "Book In",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_get_bookin_date,
    )
    
    bookout_date = fields.Datetime(
        "Book Out",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_get_bookout_date,
    )
    
    prescription_order_line = fields.One2many(
        comodel_name='prescription.order.line',
        inverse_name='prescription_order_id',
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        copy=True, auto_join=True)
    
    prescription_accommodation_line = fields.One2many(
        "prescription.accommodation.line",
        "prescription_order_id",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        help="Prescription accommodations details provided to"
        "Customer and it will included in "
        "the main Invoice.",
    )
    prescription_policy = fields.Selection(
        [
            ("prepaid", "On Booking"),
            ("manual", "On Book In"),
            ("picking", "On Bookout"),
        ],
        default="manual",
        help="Prescription policy for payment that "
        "either the guest has to payment at "
        "booking time or book-in "
        "book-out time.",
    )
    duration = fields.Float(
        "Duration in Days",
        help="Number of days which will automatically "
        "count from the book-in and book-out date. ",
    )
    prescription_invoice_id = fields.Many2one("account.move", "Invoice", copy=False)
    duration_dummy = fields.Float()

    @api.constrains("prescription_order_line")
    def _check_duplicate_order_device_line(self):
        """
        This method is used to validate the device_lines.
        ------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        for rec in self:
            for product in rec.prescription_order_line.mapped("product_id"):
                for line in rec.prescription_order_line.filtered(
                    lambda l: l.product_id == product
                ):
                    record = rec.prescription_order_line.search(
                        [
                            ("product_id", "=", product.id),
                            ("prescription_order_id", "=", rec.id),
                            ("id", "!=", line.id),
                            ("bookin_date", ">=", line.bookin_date),
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

    def _update_order_line(self, prescription_order_id):
        order_device_line_obj = self.env["order.device.line"]
        prescription_device_obj = self.env["prescription.device"]
        for rec in prescription_order_id:
            for device_rec in rec.prescription_order_line:
                device = prescription_device_obj.search(
                    [("product_id", "=", device_rec.product_id.id)]
                )
                device.write({"is_device": False})
                vals = {
                    "device_id": device.id,
                    "book_in": rec.bookin_date,
                    "book_out": rec.bookout_date,
                    "prescription_order_id": rec.id,
                }
                order_device_line_obj.create(vals)

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for prescription order.
        """
        if not "prescription_accommodation_line" and "prescription_order_id" in vals:
            tmp_device_lines = vals.get("prescription_order_line", [])
            vals["order_policy"] = vals.get("prescription_policy", "manual")
            vals.update({"prescription_order_line": []})
            prescription_order_id = super(PrescriptionOrder, self).create(vals)
            for line in tmp_device_lines:
                line[2].update({"prescription_order_id": prescription_order_id.id})
            vals.update({"prescription_order_line": tmp_device_lines})
            prescription_order_id.write(vals)
        else:
            if not vals:
                vals = {}
            vals["name"] = self.env["ir.sequence"].next_by_code("prescription.order")
            vals["duration"] = vals.get("duration", 0.0) or vals.get("duration", 0.0)
            prescription_order_id = super(PrescriptionOrder, self).create(vals)
            self._update_order_line(prescription_order_id)
        return prescription_order_id

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        product_obj = self.env["product.product"]
        prescription_device_obj = self.env["prescription.device"]
        order_device_line_obj = self.env["order.device.line"]
        for rec in self:
            devices_list = [res.product_id.id for res in rec.prescription_order_line]
            if vals and vals.get("duration", False):
                vals["duration"] = vals.get("duration", 0.0)
            else:
                vals["duration"] = rec.duration
            device_lst = [order_rec.product_id.id for order_rec in rec.prescription_order_line]
            new_devices = set(device_lst).difference(set(devices_list))
            if len(list(new_devices)) != 0:
                device_list = product_obj.browse(list(new_devices))
                for device in device_list:
                    device_obj = prescription_device_obj.search([("product_id", "=", device.id)])
                    device_obj.write({"is_device": False})
                    vals = {
                        "device_id": device_obj.id,
                        "book_in": rec.bookin_date,
                        "book_out": rec.bookout_date,
                        "prescription_order_id": rec.id,
                    }
                    order_device_line_obj.create(vals)
            if not len(list(new_devices)):
                device_list_obj = product_obj.browse(devices_list)
                for device in device_list_obj:
                    device_obj = prescription_device_obj.search([("product_id", "=", device.id)])
                    device_obj.write({"is_device": False})
                    device_vals = {
                        "device_id": device_obj.id,
                        "book_in": rec.bookin_date,
                        "book_out": rec.bookout_date,
                        "prescription_order_id": rec.id,
                    }
                    order_romline_rec = order_device_line_obj.search(
                        [("prescription_order_id", "=", rec.id)]
                    )
                    order_romline_rec.write(device_vals)
        return super(PrescriptionOrder, self).write(vals)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        """
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the prescription order as well
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
            
            # Iterate over each device line
            for device_line in rec.prescription_order_line:
                product = device_line.order_line.product_id
                devices = self.env["prescription.device"].search([("product_id", "=", product.id)])
                devices.write({"is_device": True, "status": "available"})
            
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


class PrescriptionOrderLine(models.Model):
    _name = "prescription.order.line"
    _inherit = 'analytic.mixin'
    _description = "Prescription Order Line"
    _rec_names_search = ['name', 'prescription_order_id.name']
    _order = 'prescription_order_id, sequence, id'
    _check_company_auto = True

    _sql_constraints = [
        ('accountable_required_fields',
            "CHECK(display_type IS NOT NULL OR (product_id IS NOT NULL AND product_uom IS NOT NULL))",
            "Missing required fields on accountable prescription order line."),
        ('non_accountable_null_fields',
            "CHECK(display_type IS NULL OR (product_id IS NULL AND price_unit = 0 AND product_uom_qty = 0 AND product_uom IS NULL))",
            "Forbidden values on non-accountable prescription order line"),
    ]

    order_line = fields.Many2one(
        "sale.order.line",
        "Order Line",
        required=True,
        delegate=True,
        ondelete="cascade",
        index=True,
    )
    prescription_order_id = fields.Many2one("prescription.order", "Order", ondelete="cascade")
    sequence = fields.Integer(string="Sequence", default=10)
    company_id = fields.Many2one(
        related='prescription_order_id.company_id',
        store=True, index=True, precompute=True)
    currency_id = fields.Many2one(
        related='prescription_order_id.currency_id',
        depends=['prescription_order_id.currency_id'],
        store=True, precompute=True)
    prescription_order_partner_id = fields.Many2one(
        related='prescription_order_id.partner_id',
        string="Customer",
        store=True, index=True, precompute=True)
    user_id = fields.Many2one(
        related='prescription_order_id.user_id',
        string="User",
        store=True, precompute=True)
    state = fields.Selection(
        related='prescription_order_id.state',
        string="Prescription Order Status",
        copy=False, store=True, precompute=True)
    # Fields specifying custom line logic
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)
    bookin_date = fields.Datetime("Book In", required=True)
    bookout_date = fields.Datetime("Book Out")
    is_reserved = fields.Boolean(help="True when order line created from Reservation")
    
    # Generic configuration fields
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', check_company=True, index='btree_not_null',
        domain="[('sale_ok', '=', True)]")
    product_template_id = fields.Many2one(
        string="Product Template",
        comodel_name='product.template',
        compute='_compute_product_template_id',
        readonly=False,
        search='_search_product_template_id',
        # previously related='product_id.product_tmpl_id'
        # not anymore since the field must be considered editable for product configurator logic
        # without modifying the related product_id when updated.
        domain=[('sale_ok', '=', True)])
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', depends=['product_id'])
    product_custom_attribute_value_ids = fields.Many2many(
        comodel_name='product.attribute.custom.value',
        relation='prescription_order_line_rel',   
        inverse_name='prescription_order_line',
        string="Custom Values",
        compute='_compute_custom_attribute_values',
        store=True, readonly=False, precompute=True, copy=True
    )
    # M2M holding the values of product.attribute with create_variant field set to 'no_variant'
    # It allows keeping track of the extra_price associated to those attribute values and add them to the RX line description
    product_no_variant_attribute_value_ids = fields.Many2many(
        comodel_name='product.template.attribute.value',
        string="Extra Values",
        compute='_compute_no_variant_attribute_values',
        store=True, readonly=False, precompute=True, ondelete='restrict')

    name = fields.Text(
        string="Description",
        compute='_compute_name',
        store=True, readonly=False, required=True, precompute=True)

    product_uom_qty = fields.Float(
        string="Quantity",
        compute='_compute_product_uom_qty',
        digits='Product Unit of Measure', default=1.0,
        store=True, readonly=False, required=True, precompute=True)
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute='_compute_product_uom',
        store=True, readonly=False, precompute=True, ondelete='restrict',
        domain="[('category_id', '=', product_uom_category_id)]")
    product_type = fields.Selection(related='product_id.detailed_type', depends=['product_id'])
    # product_updatable = fields.Boolean(
    #     string="Can Edit Product",
    #     compute='_compute_product_updatable')
    product_updatable = fields.Boolean(compute='_compute_product_updatable', string='Can Edit Product', default=True)
    product_uom_readonly = fields.Boolean(
        compute='_compute_product_uom_readonly')

    #=== COMPUTE METHODS ===#

    @api.depends('prescription_order_partner_id', 'prescription_order_id', 'product_id')
    def _compute_display_name(self):
        name_per_id = self._additional_name_per_id()
        for rx_line in self.sudo():
            name = '{} - {}'.format(rx_line.prescription_order_id.name, rx_line.name and rx_line.name.split('\n')[0] or rx_line.product_id.name)
            additional_name = name_per_id.get(rx_line.id)
            if additional_name:
                name = f'{name} {additional_name}'
            rx_line.display_name = name

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id

    def _search_product_template_id(self, operator, value):
        return [('product_id.product_tmpl_id', operator, value)]

    @api.depends('product_id')
    def _compute_custom_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.product_custom_attribute_value_ids = False
                continue
            if not line.product_custom_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            for pacv in line.product_custom_attribute_value_ids:
                if pacv.custom_product_template_attribute_value_id not in valid_values:
                    line.product_custom_attribute_value_ids -= pacv

    @api.depends('product_id')
    def _compute_no_variant_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.product_no_variant_attribute_value_ids = False
                continue
            if not line.product_no_variant_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            for ptav in line.product_no_variant_attribute_value_ids:
                if ptav._origin not in valid_values:
                    line.product_no_variant_attribute_value_ids -= ptav

    # @api.depends('product_id')
    # def _compute_name(self):
    #     for line in self:
    #         if not line.product_id:
    #             continue
    #         if not line.prescription_order_partner_id.is_public:
    #             line = line.with_context(lang=line.prescription_order_partner_id.lang)
    #         name = line._get_sale_order_line_multiline_description_sale()
    #         if not line.display_type:
    #             context = {'lang': line.prescription_order_partner_id.lang}
    #             del context
    #         line.name = name


    @api.depends('prescription_order_id')
    def _compute_name(self):
        """Override to add the compute dependency.

        The custom name logic can be found below in _get_sale_order_line_multiline_description_sale.
        """
        super()._compute_name()


    # def _get_sale_order_line_multiline_description_sale(self):

    #     self.ensure_one()
    #     return self.product_id.get_product_multiline_description_sale() + self._get_sale_order_line_multiline_description_variants()

    def _get_sale_order_line_multiline_description_sale(self):
        if self.prescription_order_id:
            return self.prescription_order_id._get_order_multiline_description() + self._get_sale_order_line_multiline_description_variants()
        else:
            return super()._get_sale_order_line_multiline_description_sale()

    # def _get_prescription_order_line_multiline_description_sale(self):
    #     self.ensure_one()
    #     return self.product_id.get_product_multiline_description_sale() + self._get_prescription_order_line_multiline_description_variants()

    # def _get_prescription_order_line_multiline_description_variants(self):
    #     if not self.product_custom_attribute_value_ids and not self.product_no_variant_attribute_value_ids:
    #         return ""

    #     name = "\n"

    #     custom_ptavs = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id
    #     no_variant_ptavs = self.product_no_variant_attribute_value_ids._origin
    #     multi_ptavs = no_variant_ptavs.filtered(lambda ptav: ptav.display_type == 'multi').sorted()
    #     for ptav in (no_variant_ptavs - multi_ptavs - custom_ptavs):
    #         name += "\n" + ptav.display_name
    #     for pta, ptavs in groupby(multi_ptavs, lambda ptav: ptav.attribute_id):
    #         name += "\n" + _(
    #             "%(attribute)s: %(values)s",
    #             attribute=pta.name,
    #             values=", ".join(ptav.name for ptav in ptavs)
    #         )
    #     sorted_custom_ptav = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id.sorted()
    #     for patv in sorted_custom_ptav:
    #         pacv = self.product_custom_attribute_value_ids.filtered(lambda pcav: pcav.custom_product_template_attribute_value_id == patv)
    #         name += "\n" + pacv.display_name

    #     return name

    #=== CRUD METHODS ===#
    @api.depends('product_id', 'prescription_order_id.state')
    def _compute_product_updatable(self):
        for line in self:
            if line.state in ['done', 'cancel']:
                line.product_updatable = False
            else:
                line.product_updatable = True
                

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for prescription order line.
        """
        if "prescription_order_id" in vals:
            prescription = self.env["prescription.order"].browse(vals["prescription_order_id"])
            vals.update({"order_id": prescription.order_id.id})
        return super(PrescriptionOrderLine, self).create(vals)


    #=== ACTION METHODS ===#

    def action_add_from_catalog(self):
        prescription_order = self.env['prescription.order'].browse(self.env.context.get('prescription_order_id'))
        return prescription_order.action_add_from_catalog()

    #=== CORE METHODS OVERRIDES ===#

    def _get_partner_display(self):
        self.ensure_one()
        commercial_partner = self.prescription_order_partner_id.commercial_partner_id
        return f'({commercial_partner.ref or commercial_partner.name})'

    def _additional_name_per_id(self):
        return {
            rx_line.id: rx_line._get_partner_display()
            for rx_line in self
        }

    def _get_product_catalog_lines_data(self, **kwargs):

        if len(self) == 1:
            return {
                'quantity': self.product_uom_qty,
                'price': self.price_unit,
                'readOnly': self.prescription_order_id._is_readonly(),
            }
        elif self:
            self.product_id.ensure_one()
            prescription_order_line = self[0]
            prescription_order = prescription_order_line.prescription_order_id
            return {
                'readOnly': True,
                'price': prescription_order.pricelist_id._get_product_price(
                    product=prescription_order_line.product_id,
                    quantity=1.0,
                    currency=prescription_order.currency_id,
                    date=prescription_order.date_order,
                    **kwargs,
                ),
                'quantity': sum(
                    self.mapped(
                        lambda line: line.product_uom._compute_quantity(
                            qty=line.product_uom_qty,
                            to_unit=line.product_id.uom_id,
                        )
                    )
                ),
            }
        else:
            return {
                'quantity': 0,
                # price will be computed in batch with pricelist utils so not given here
            }


    @api.constrains("bookin_date", "bookout_date")
    def _check_dates(self):
        """
        This method is used to validate the bookin_date and bookout_date.
        -------------------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        if self.bookin_date >= self.bookout_date:
            raise ValidationError(
                _(
                    """Device line Book In Date Should be """
                    """less than the Book Out Date!"""
                )
            )
        if self.prescription_order_id.date_order and self.bookin_date:
            if self.bookin_date.date() < self.prescription_order_id.date_order.date():
                raise ValidationError(
                    _(
                        """Device line book in date should be """
                        """greater than the current date."""
                    )
                )

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        for line in self:
            if line.order_line:
                devices = self.env["prescription.device"].search(
                    [("product_id", "=", line.order_line.product_id.id)]
                )
                order_device_lines = self.env["order.device.line"].search(
                    [
                        ("prescription_order_id", "=", line.prescription_order_id.id),
                        ("device_id", "in", devices.ids),
                    ]
                )
                order_device_lines.unlink()
                devices.write({"is_device": True, "status": "available"})
                line.order_line.unlink()
        return super(PrescriptionOrderLine, self).unlink()

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        # if self._context.get("parent_variant_qty"):
        #     qty = self._context.get("parent_variant_qty")
        #     product = product.with_context(quantity=qty)

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
                    ).get_product_price_rule(product, qty, self.prescription_order_id.partner_id)
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
        if self.prescription_order_id.pricelist_id.discount_policy == "with_discount":
            return product.with_context(pricelist=self.prescription_order_id.pricelist_id.id).price
        product_context = dict(
            self.env.context,
            partner_id=self.prescription_order_id.partner_id.id,
            date=self.prescription_order_id.date_order,
            uom=self.product_uom.id,
        )
        final_price, rule_id = self.prescription_order_id.pricelist_id.with_context(
            **product_context
        ).get_product_price_rule(
            self.product_id,
            self.product_uom_qty or 1.0,
            self.prescription_order_id.partner_id,
        )
        base_price, currency_id = self.with_context(
            **product_context
        )._get_real_price_currency(
            product,
            rule_id,
            self.product_uom_qty,
            self.product_uom,
            self.prescription_order_id.pricelist_id.id,
        )
        if currency_id != self.prescription_order_id.pricelist_id.currency_id.id:
            base_price = (
                self.env["res.currency"]
                .browse(currency_id)
                .with_context(**product_context)
                .compute(base_price, self.prescription_order_id.pricelist_id.currency_id)
            )
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = (
                line.order_id.fiscal_position_id
                or line.order_id.fiscal_position_id._get_fiscal_position(
                    line.prescription_order_partner_id.id
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
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

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
            name=self.order_line._get_sale_order_line_multiline_description_sale()
        )
        
        self._compute_tax_id()

        if self.prescription_order_id.pricelist_id and self.prescription_order_id.partner_id:
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
    #     configured_addition_hours = (
    #         self.prescription_order_id.warehouse_id.company_id.additional_hours
    #     )
    #     myduration = 0
    #     if self.bookin_date and self.bookout_date:
    #         dur = self.bookout_date - self.bookin_date
    #         sec_dur = dur.seconds
    #         if (not dur.days and not sec_dur) or (dur.days and not sec_dur):
    #             myduration = dur.days
    #         else:
    #             myduration = dur.days + 1
    #         if configured_addition_hours > 0:
    #             additional_hours = abs((dur.seconds / 60) / 60)
    #             if additional_hours >= configured_addition_hours:
    #                 myduration += 1
    #     self.product_uom_qty = myduration

    def copy_data(self, default=None):
        """
        @param self: object pointer
        @param default: dict of default values to be set
        """

        sale_line_obj = self.order_line
        return sale_line_obj.copy_data(default=default)


class PrescriptionAccommodationLine(models.Model):

    _name = "prescription.accommodation.line"
    _description = "prescription Accommodation line"

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        """
        @param self: object pointer
        @param default: dict of default values to be set
        """
        return super(PrescriptionAccommodationLine, self).copy(default=default)

    accommodation_line_id = fields.Many2one(
        "sale.order.line",
        "Accommodation Line",
        delegate=True,
        ondelete="cascade",
    )
    prescription_order_id = fields.Many2one("prescription.order", "Order", ondelete="cascade")
    accomm_bookin_date = fields.Datetime("From Date")
    accomm_bookout_date = fields.Datetime("To Date")

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for prescription accommodation line.
        """
        if "prescription_order_id" in vals:
            prescription = self.env["prescription.order"].browse(vals["prescription_order_id"])
            vals.update({"order_id": prescription.order_id.id})
        return super(PrescriptionAccommodationLine, self).create(vals)

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
                line.prescription_order_id.fiscal_position_id
                or line.prescription_order_id.partner_id.property_account_position_id
            )
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(
                lambda r: not line.company_id or r.company_id == line.company_id
            )
            line.tax_id = (
                fpos.map_tax(taxes, line.product_id, line.prescription_order_id.partner_shipping_id)
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
                    ).get_product_price_rule(product, qty, self.prescription_order_id.partner_id)
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
        if self.prescription_order_id.pricelist_id.discount_policy == "with_discount":
            return product.with_context(pricelist=self.prescription_order_id.pricelist_id.id).price
        product_context = dict(
            self.env.context,
            partner_id=self.prescription_order_id.partner_id.id,
            date=self.prescription_order_id.date_order,
            uom=self.product_uom.id,
        )
        final_price, rule_id = self.prescription_order_id.pricelist_id.with_context(
            **product_context
        ).get_product_price_rule(
            self.product_id,
            self.product_uom_qty or 1.0,
            self.prescription_order_id.partner_id,
        )
        base_price, currency_id = self.with_context(
            **product_context
        )._get_real_price_currency(
            product,
            rule_id,
            self.product_uom_qty,
            self.product_uom,
            self.prescription_order_id.pricelist_id.id,
        )
        if currency_id != self.prescription_order_id.pricelist_id.currency_id.id:
            base_price = (
                self.env["res.currency"]
                .browse(currency_id)
                .with_context(**product_context)
                .compute(base_price, self.prescription_order_id.pricelist_id.currency_id)
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
            name=self.accommodation_line_id._get_sale_order_line_multiline_description_sale(product)
        )
        
        self._compute_tax_id()

        if self.prescription_order_id.pricelist_id and self.prescription_order_id.partner_id:
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

    # @api.onchange("accomm_bookin_date", "accomm_bookout_date")
    # def _on_change_bookin_bookout_dates(self):
    #     if not self.accomm_bookin_date:
    #         time_a = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    #         self.accomm_bookin_date = time_a
    #     if not self.accomm_bookout_date:
    #         self.accomm_bookout_date = time_a
    #     if self.accomm_bookout_date < self.accomm_bookin_date:
    #         raise ValidationError(_("Bookout must be greater or equal bookin date"))
    #     if self.accomm_bookin_date and self.accomm_bookout_date:
    #         diffDate = self.accomm_bookout_date - self.accomm_bookin_date
    #         qty = diffDate.days + 1
    #         self.product_uom_qty = qty

    def copy_data(self, default=None):
        """
        @param self: object pointer
        @param default: dict of default values to be set
        """
        return self.accommodation_line_id.copy_data(default=default)
