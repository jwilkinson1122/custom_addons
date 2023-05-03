# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class AccountPractice(models.Model):

    _name = "account.practice"
    _description = "Practice"
    _order = "sequence"

    name = fields.Char("Practice Name", required=True, index=True)
    sequence = fields.Integer("sequence", default=10)


class AccountDevice(models.Model):

    _name = "account.device"
    _description = "Account Device"

    product_id = fields.Many2one(
        "product.product",
        "Product_id",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    practice_id = fields.Many2one(
        "account.practice",
        "Practice No",
        help="At which practice the device is located.",
        ondelete="restrict",
    )
    max_qty = fields.Integer()
    min_qty = fields.Integer()
    device_categ_id = fields.Many2one(
        "account.device.type", "Device Category", required=True, ondelete="restrict"
    )
    device_customization_ids = fields.Many2many(
        "account.device.customization", string="Device Customization", help="List of device customization."
    )
    status = fields.Selection(
        [("available", "Available"), ("unavailable", "Unavailable")],
        default="available",
    )
    quantity = fields.Integer(required=True)
    device_line_ids = fields.One2many(
        "prescription.device.line", "device_id", string="Device Line"
    )
    laterality =fields.Selection([
		('lt', 'Left Only'),
		('rt', 'Right Only'),
        ('bl', 'Bilateral'),
  ],
		string='Laterality',required=True)
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "device_categ_id" in vals:
            device_categ = self.env["account.device.type"].browse(vals.get("device_categ_id"))
            vals.update({"categ_id": device_categ.product_categ_id.id})
        return super(AccountDevice, self).create(vals)

    @api.constrains("quantity")
    def _book_quantity(self):
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
            device_categ = self.env["account.device.type"].browse(vals.get("device_categ_id"))
            vals.update({"categ_id": device_categ.product_categ_id.id})
        if "is_device" in vals and vals["is_device"] is False:
            vals.update({"color": 2, "status": "unavailable"})
        if "is_device" in vals and vals["is_device"] is True:
            vals.update({"color": 5, "status": "available"})
        return super(AccountDevice, self).write(vals)

    def set_device_status_unavailable(self):
        """
        This method is used to change the state
        to unavailable of the account device.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"is_device": False, "color": 2})

    def set_device_status_available(self):
        """
        This method is used to change the state
        to available of the account device.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"is_device": True, "color": 5})


class AccountDeviceType(models.Model):

    _name = "account.device.type"
    _description = "Device Type"

    categ_id = fields.Many2one("account.device.type", "Category")
    child_ids = fields.One2many("account.device.type", "categ_id", "Device Child Categories")
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
            device_categ = self.env["account.device.type"].browse(vals.get("categ_id"))
            vals.update({"parent_id": device_categ.product_categ_id.id})
        return super(AccountDeviceType, self).create(vals)

    def write(self, vals):
        if "categ_id" in vals:
            device_categ = self.env["account.device.type"].browse(vals.get("categ_id"))
            vals.update({"parent_id": device_categ.product_categ_id.id})
        return super(AccountDeviceType, self).write(vals)

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


class AccountDeviceCustomizationType(models.Model):

    _name = "account.device.customization.type"
    _description = "customization Type"

    customization_id = fields.Many2one("account.device.customization.type", "Category")
    child_ids = fields.One2many(
        "account.device.customization.type", "customization_id", "Customization Child Categories"
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
        if "customization_id" in vals:
            customization_categ = self.env["account.device.customization.type"].browse(
                vals.get("customization_id")
            )
            vals.update({"parent_id": customization_categ.product_categ_id.id})
        return super(AccountDeviceCustomizationType, self).create(vals)

    def write(self, vals):
        if "customization_id" in vals:
            customization_categ = self.env["account.device.customization.type"].browse(
                vals.get("customization_id")
            )
            vals.update({"parent_id": customization_categ.product_categ_id.id})
        return super(AccountDeviceCustomizationType, self).write(vals)

    def name_get(self):
        def get_names(cat):
            """Return the list [cat.name, cat.customization_id.name, ...]"""
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.customization_id
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
                        [[("customization_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("customization_id", "in", category_ids)], domain]
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


class AccountDeviceCustomization(models.Model):

    _name = "account.device.customization"
    _description = "Device customization"

    product_id = fields.Many2one(
        "product.product",
        "Device Customization Product",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    customization_categ_id = fields.Many2one(
        "account.device.customization.type",
        "Customization Category",
        required=True,
        ondelete="restrict",
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "customization_categ_id" in vals:
            customization_categ = self.env["account.device.customization.type"].browse(
                vals.get("customization_categ_id")
            )
            vals.update({"categ_id": customization_categ.product_categ_id.id})
        return super(AccountDeviceCustomization, self).create(vals)

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "customization_categ_id" in vals:
            customization_categ = self.env["account.device.customization.type"].browse(
                vals.get("customization_categ_id")
            )
            vals.update({"categ_id": customization_categ.product_categ_id.id})
        return super(AccountDeviceCustomization, self).write(vals)
