# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression

 


class PodiatryDevice(models.Model):

    _name = "podiatry.device"
    _description = "Podiatry Device"

    product_id = fields.Many2one(
        "product.product",
        "Product_id",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
 
    max_adult = fields.Integer()
    max_child = fields.Integer()
    device_categ_id = fields.Many2one(
        "podiatry.device.type", "Device Category", required=True, ondelete="restrict"
    )
    device_items_ids = fields.Many2many(
        "podiatry.device.items", string="Device Items", help="List of device items."
    )
    status = fields.Selection(
        [("available", "Available"), ("unavailable", "Unavailable")],
        default="available",
    )
    capacity = fields.Integer(required=True)
    device_line_ids = fields.One2many(
        "prescription.device.line", "device_id", string="Device Reservation Line"
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "device_categ_id" in vals:
            device_categ = self.env["podiatry.device.type"].browse(vals.get("device_categ_id"))
            vals.update({"categ_id": device_categ.product_categ_id.id})
        return super(PodiatryDevice, self).create(vals)

    @api.constrains("capacity")
    def _check_capacity(self):
        for device in self:
            if device.capacity <= 0:
                raise ValidationError(_("Device capacity must be more than 0"))

    @api.onchange("isdevice")
    def _isdevice_change(self):
        """
        Based on isdevice, status will be updated.
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
            device_categ = self.env["podiatry.device.type"].browse(vals.get("device_categ_id"))
            vals.update({"categ_id": device_categ.product_categ_id.id})
        if "isdevice" in vals and vals["isdevice"] is False:
            vals.update({"color": 2, "status": "unavailable"})
        if "isdevice" in vals and vals["isdevice"] is True:
            vals.update({"color": 5, "status": "available"})
        return super(PodiatryDevice, self).write(vals)

    def set_device_status_unavailable(self):
        """
        This method is used to change the state
        to unavailable of the podiatry device.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"isdevice": False, "color": 2})

    def set_device_status_available(self):
        """
        This method is used to change the state
        to available of the podiatry device.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"isdevice": True, "color": 5})


class PodiatryDeviceType(models.Model):

    _name = "podiatry.device.type"
    _description = "Device Type"

    categ_id = fields.Many2one("podiatry.device.type", "Category")
    child_ids = fields.One2many("podiatry.device.type", "categ_id", "Device Child Categories")
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
            device_categ = self.env["podiatry.device.type"].browse(vals.get("categ_id"))
            vals.update({"parent_id": device_categ.product_categ_id.id})
        return super(PodiatryDeviceType, self).create(vals)

    def write(self, vals):
        if "categ_id" in vals:
            device_categ = self.env["podiatry.device.type"].browse(vals.get("categ_id"))
            vals.update({"parent_id": device_categ.product_categ_id.id})
        return super(PodiatryDeviceType, self).write(vals)

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


class PodiatryDeviceItemsType(models.Model):

    _name = "podiatry.device.items.type"
    _description = "items Type"

    item_id = fields.Many2one("podiatry.device.items.type", "Category")
    child_ids = fields.One2many(
        "podiatry.device.items.type", "item_id", "Items Child Categories"
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
        if "item_id" in vals:
            item_categ = self.env["podiatry.device.items.type"].browse(
                vals.get("item_id")
            )
            vals.update({"parent_id": item_categ.product_categ_id.id})
        return super(PodiatryDeviceItemsType, self).create(vals)

    def write(self, vals):
        if "item_id" in vals:
            item_categ = self.env["podiatry.device.items.type"].browse(
                vals.get("item_id")
            )
            vals.update({"parent_id": item_categ.product_categ_id.id})
        return super(PodiatryDeviceItemsType, self).write(vals)

    def name_get(self):
        def get_names(cat):
            """Return the list [cat.name, cat.item_id.name, ...]"""
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.item_id
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
                        [[("item_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("item_id", "in", category_ids)], domain]
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


class PodiatryDeviceItems(models.Model):

    _name = "podiatry.device.items"
    _description = "Device items"

    product_id = fields.Many2one(
        "product.product",
        "Device Items Product",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    items_categ_id = fields.Many2one(
        "podiatry.device.items.type",
        "Items Category",
        required=True,
        ondelete="restrict",
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "items_categ_id" in vals:
            items_categ = self.env["podiatry.device.items.type"].browse(
                vals.get("items_categ_id")
            )
            vals.update({"categ_id": items_categ.product_categ_id.id})
        return super(PodiatryDeviceItems, self).create(vals)

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "items_categ_id" in vals:
            items_categ = self.env["podiatry.device.items.type"].browse(
                vals.get("items_categ_id")
            )
            vals.update({"categ_id": items_categ.product_categ_id.id})
        return super(PodiatryDeviceItems, self).write(vals)
