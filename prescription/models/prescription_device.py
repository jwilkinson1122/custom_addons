# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class PrescriptionLaterality(models.Model):

    _name = "prescription.laterality"
    _description = "Laterality"
    _order = "sequence"

    name = fields.Char("Laterality Name", required=True, index=True)
    sequence = fields.Integer("sequence", default=10)


class PrescriptionDevice(models.Model):

    _name = "prescription.device"
    _description = "Prescription Device"

    product_id = fields.Many2one(
        "product.product",
        "Product_id",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    laterality_id = fields.Many2one(
        "prescription.laterality",
        "Laterality No",
        help="At which laterality the device is located.",
        ondelete="restrict",
    )
    device_categ_id = fields.Many2one(
        "prescription.device.type", "Device Category", required=True, ondelete="restrict"
    )
    device_options_ids = fields.Many2many(
        "prescription.device.options", string="Device Options", help="List of device options."
    )
    status = fields.Selection(
        [("available", "Available"), ("unavailable", "Occupied")],
        default="available",
    )
    prescription_line = fields.One2many(
        "order.device.line", "device_id", string="Device Reservation Line"
    )
    product_manager = fields.Many2one("res.users")
    
    quantity = fields.Float(string='Quantity', digits='Product Quantity')


    @api.model
    def create(self, vals):
        if "device_categ_id" in vals:
            device_categ = self.env["prescription.device.type"].browse(vals.get("device_categ_id"))
            vals.update({"categ_id": device_categ.product_categ_id.id})
        return super(PrescriptionDevice, self).create(vals)

    @api.constrains("quantity")
    def _check_quantity(self):
        for device in self:
            if device.quantity <= 0:
                raise ValidationError(_("Device quantity must be more than 0"))

    @api.onchange("is_device")
    def _is_device_change(self):
        """
        Based on is_device, status will be updated.
        ----------------------------------------
        @param self: object pointer
        """
        self.status = "available" if self.status else "unavailable"

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "device_categ_id" in vals:
            device_categ = self.env["prescription.device.type"].browse(vals.get("device_categ_id"))
            vals.update({"categ_id": device_categ.product_categ_id.id})
        if "is_device" in vals and vals["is_device"] is False:
            vals.update({"color": 2, "status": "unavailable"})
        if "is_device" in vals and vals["is_device"] is True:
            vals.update({"color": 5, "status": "available"})
        return super(PrescriptionDevice, self).write(vals)

    def set_device_status_unavailable(self):
        """
        This method is used to change the state
        to unavailable of the prescription device.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"is_device": False, "color": 2})

    def set_device_status_available(self):
        """
        This method is used to change the state
        to available of the prescription device.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"is_device": True, "color": 5})


class PrescriptionDeviceType(models.Model):

    _name = "prescription.device.type"
    _description = "Device Type"

    categ_id = fields.Many2one("prescription.device.type", "Category")
    child_ids = fields.One2many("prescription.device.type", "categ_id", "Device Child Categories")
    product_categ_id = fields.Many2one(
        "product.category",
        "Product Category",
        delegate=True,
        required=True,
        copy=False,
        ondelete="restrict",
    )

    @api.model
    def create(self, vals):
        if "categ_id" in vals:
            device_categ = self.env["prescription.device.type"].browse(vals.get("categ_id"))
            vals.update({"parent_id": device_categ.product_categ_id.id})
        return super(PrescriptionDeviceType, self).create(vals)

    def write(self, vals):
        if "categ_id" in vals:
            device_categ = self.env["prescription.device.type"].browse(vals.get("categ_id"))
            vals.update({"parent_id": device_categ.product_categ_id.id})
        return super(PrescriptionDeviceType, self).write(vals)

    def name_get(self):
        def get_names(cat):
            """Return the list [cat.name, cat.categ_id.name, ...]"""
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.categ_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symmetric to name_get
            category_names = name.split(" / ")
            parents = list(category_names)
            child = parents.pop()
            domain = [("name", operator, child)]
            if parents:
                names_ids = self.name_search(
                    " / ".join(parents),
                    args=args,
                    operator="ilike",
                    limit=limit,
                )
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([("id", "not in", category_ids)])
                    domain = expression.OR(
                        [[("categ_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("categ_id", "in", category_ids)], domain]
                    )
                for i in range(1, len(category_names)):
                    domain = [
                        [
                            (
                                "name",
                                operator,
                                " / ".join(category_names[-1 - i :]),
                            )
                        ],
                        domain,
                    ]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()


class PrescriptionDeviceOptionsType(models.Model):

    _name = "prescription.device.options.type"
    _description = "options Type"

    option_id = fields.Many2one("prescription.device.options.type", "Category")
    child_ids = fields.One2many(
        "prescription.device.options.type", "option_id", "Options Child Categories"
    )
    product_categ_id = fields.Many2one(
        "product.category",
        "Product Category",
        delegate=True,
        required=True,
        copy=False,
        ondelete="restrict",
    )

    @api.model
    def create(self, vals):
        if "option_id" in vals:
            option_categ = self.env["prescription.device.options.type"].browse(
                vals.get("option_id")
            )
            vals.update({"parent_id": option_categ.product_categ_id.id})
        return super(PrescriptionDeviceOptionsType, self).create(vals)

    def write(self, vals):
        if "option_id" in vals:
            option_categ = self.env["prescription.device.options.type"].browse(
                vals.get("option_id")
            )
            vals.update({"parent_id": option_categ.product_categ_id.id})
        return super(PrescriptionDeviceOptionsType, self).write(vals)

    def name_get(self):
        def get_names(cat):
            """Return the list [cat.name, cat.option_id.name, ...]"""
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.option_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(" / ")
            parents = list(category_names)
            child = parents.pop()
            domain = [("name", operator, child)]
            if parents:
                names_ids = self.name_search(
                    " / ".join(parents),
                    args=args,
                    operator="ilike",
                    limit=limit,
                )
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([("id", "not in", category_ids)])
                    domain = expression.OR(
                        [[("option_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("option_id", "in", category_ids)], domain]
                    )
                for i in range(1, len(category_names)):
                    domain = [
                        [
                            (
                                "name",
                                operator,
                                " / ".join(category_names[-1 - i :]),
                            )
                        ],
                        domain,
                    ]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()


class PrescriptionDeviceOptions(models.Model):

    _name = "prescription.device.options"
    _description = "Device options"

    product_id = fields.Many2one(
        "product.product",
        "Device Options Product",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    options_categ_id = fields.Many2one(
        "prescription.device.options.type",
        "Options Category",
        required=True,
        ondelete="restrict",
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "options_categ_id" in vals:
            options_categ = self.env["prescription.device.options.type"].browse(
                vals.get("options_categ_id")
            )
            vals.update({"categ_id": options_categ.product_categ_id.id})
        return super(PrescriptionDeviceOptions, self).create(vals)

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "options_categ_id" in vals:
            options_categ = self.env["prescription.device.options.type"].browse(
                vals.get("options_categ_id")
            )
            vals.update({"categ_id": options_categ.product_categ_id.id})
        return super(PrescriptionDeviceOptions, self).write(vals)
