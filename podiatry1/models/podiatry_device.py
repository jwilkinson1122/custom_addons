# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class PodiatryFloor(models.Model):

    _name = "podiatry.floor"
    _description = "Floor"
    _order = "sequence"

    name = fields.Char("Floor Name", required=True, index=True)
    sequence = fields.Integer("sequence", default=10)


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
    floor_id = fields.Many2one(
        "podiatry.floor",
        "Floor No",
        help="At which floor the device is located.",
        ondelete="restrict",
    )
    max_adult = fields.Integer()
    max_child = fields.Integer()
    device_categ_id = fields.Many2one(
        "podiatry.device.type", "Device Category", required=True, ondelete="restrict"
    )
    device_accommodations_ids = fields.Many2many(
        "podiatry.device.accommodations", string="Device Accommodations", help="List of device accommodations."
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
            device_categ = self.env["podiatry.device.type"].browse(
                vals.get("device_categ_id"))
            vals.update({"categ_id": device_categ.product_categ_id.id})
        return super(PodiatryDevice, self).create(vals)

    @api.constrains("capacity")
    def _check_capacity(self):
        for device in self:
            if device.capacity <= 0:
                raise ValidationError(_("Device capacity must be more than 0"))

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
            device_categ = self.env["podiatry.device.type"].browse(
                vals.get("device_categ_id"))
            vals.update({"categ_id": device_categ.product_categ_id.id})
        if "is_device" in vals and vals["is_device"] is False:
            vals.update({"color": 2, "status": "unavailable"})
        if "is_device" in vals and vals["is_device"] is True:
            vals.update({"color": 5, "status": "available"})
        return super(PodiatryDevice, self).write(vals)

    def set_device_status_unavailable(self):
        """
        This method is used to change the state
        to unavailable of the podiatry device.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"is_device": False, "color": 2})

    def set_device_status_available(self):
        """
        This method is used to change the state
        to available of the podiatry device.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"is_device": True, "color": 5})


class PodiatryDeviceType(models.Model):

    _name = "podiatry.device.type"
    _description = "Device Type"

    categ_id = fields.Many2one("podiatry.device.type", "Category")
    child_ids = fields.One2many(
        "podiatry.device.type", "categ_id", "Device Child Categories")
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
            device_categ = self.env["podiatry.device.type"].browse(
                vals.get("categ_id"))
            vals.update({"parent_id": device_categ.product_categ_id.id})
        return super(PodiatryDeviceType, self).create(vals)

    def write(self, vals):
        if "categ_id" in vals:
            device_categ = self.env["podiatry.device.type"].browse(
                vals.get("categ_id"))
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
                                " / ".join(category_names[-1 - i:]),
                            )
                        ],
                        domain,
                    ]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(
                expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()


class PodiatryDeviceAccommodationsType(models.Model):

    _name = "podiatry.device.accommodations.type"
    _description = "accommodations Type"

    accommodation_id = fields.Many2one(
        "podiatry.device.accommodations.type", "Category")
    child_ids = fields.One2many(
        "podiatry.device.accommodations.type", "accommodation_id", "Accommodations Child Categories"
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
        if "accommodation_id" in vals:
            accommodation_categ = self.env["podiatry.device.accommodations.type"].browse(
                vals.get("accommodation_id")
            )
            vals.update({"parent_id": accommodation_categ.product_categ_id.id})
        return super(PodiatryDeviceAccommodationsType, self).create(vals)

    def write(self, vals):
        if "accommodation_id" in vals:
            accommodation_categ = self.env["podiatry.device.accommodations.type"].browse(
                vals.get("accommodation_id")
            )
            vals.update({"parent_id": accommodation_categ.product_categ_id.id})
        return super(PodiatryDeviceAccommodationsType, self).write(vals)

    def name_get(self):
        def get_names(cat):
            """Return the list [cat.name, cat.accommodation_id.name, ...]"""
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.accommodation_id
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
                        [[("accommodation_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("accommodation_id", "in", category_ids)], domain]
                    )
                for i in range(1, len(category_names)):
                    domain = [
                        [
                            (
                                "name",
                                operator,
                                " / ".join(category_names[-1 - i:]),
                            )
                        ],
                        domain,
                    ]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(
                expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()


class PodiatryDeviceAccommodations(models.Model):

    _name = "podiatry.device.accommodations"
    _description = "Device accommodations"

    product_id = fields.Many2one(
        "product.product",
        "Device Accommodations Product",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    accommodations_categ_id = fields.Many2one(
        "podiatry.device.accommodations.type",
        "Accommodations Category",
        required=True,
        ondelete="restrict",
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "accommodations_categ_id" in vals:
            accommodations_categ = self.env["podiatry.device.accommodations.type"].browse(
                vals.get("accommodations_categ_id")
            )
            vals.update({"categ_id": accommodations_categ.product_categ_id.id})
        return super(PodiatryDeviceAccommodations, self).create(vals)

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "accommodations_categ_id" in vals:
            accommodations_categ = self.env["podiatry.device.accommodations.type"].browse(
                vals.get("accommodations_categ_id")
            )
            vals.update({"categ_id": accommodations_categ.product_categ_id.id})
        return super(PodiatryDeviceAccommodations, self).write(vals)
