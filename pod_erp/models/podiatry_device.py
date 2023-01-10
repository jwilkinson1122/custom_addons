# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


# class PodiatryFloor(models.Model):

#     _name = "podiatry.floor"
#     _description = "Floor"
#     _order = "sequence"

#     name = fields.Char("Floor Name", required=True, index=True)
#     sequence = fields.Integer("sequence", default=10)


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
    # floor_id = fields.Many2one(
    #     "podiatry.floor",
    #     "Floor No",
    #     help="At which floor the device is located.",
    #     ondelete="restrict",
    # )
    max_adult = fields.Integer()
    max_child = fields.Integer()
    device_categ_id = fields.Many2one(
        "podiatry.device.type", "Device Category", required=True, ondelete="restrict"
    )
    device_amenities_ids = fields.Many2many(
        "podiatry.device.amenities", string="Device Amenities", help="List of device amenities."
    )
    status = fields.Selection(
        [("available", "Available"), ("occupied", "Occupied")],
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
        self.status = "available" if self.status else "occupied"

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
            vals.update({"color": 2, "status": "occupied"})
        if "isdevice" in vals and vals["isdevice"] is True:
            vals.update({"color": 5, "status": "available"})
        return super(PodiatryDevice, self).write(vals)

    def set_device_status_occupied(self):
        """
        This method is used to change the state
        to occupied of the podiatry device.
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


class PodiatryDeviceAmenitiesType(models.Model):

    _name = "podiatry.device.amenities.type"
    _description = "amenities Type"

    amenity_id = fields.Many2one("podiatry.device.amenities.type", "Category")
    child_ids = fields.One2many(
        "podiatry.device.amenities.type", "amenity_id", "Amenities Child Categories"
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
        if "amenity_id" in vals:
            amenity_categ = self.env["podiatry.device.amenities.type"].browse(
                vals.get("amenity_id")
            )
            vals.update({"parent_id": amenity_categ.product_categ_id.id})
        return super(PodiatryDeviceAmenitiesType, self).create(vals)

    def write(self, vals):
        if "amenity_id" in vals:
            amenity_categ = self.env["podiatry.device.amenities.type"].browse(
                vals.get("amenity_id")
            )
            vals.update({"parent_id": amenity_categ.product_categ_id.id})
        return super(PodiatryDeviceAmenitiesType, self).write(vals)

    def name_get(self):
        def get_names(cat):
            """Return the list [cat.name, cat.amenity_id.name, ...]"""
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.amenity_id
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
                        [[("amenity_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("amenity_id", "in", category_ids)], domain]
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


class PodiatryDeviceAmenities(models.Model):

    _name = "podiatry.device.amenities"
    _description = "Device amenities"

    product_id = fields.Many2one(
        "product.product",
        "Device Amenities Product",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    amenities_categ_id = fields.Many2one(
        "podiatry.device.amenities.type",
        "Amenities Category",
        required=True,
        ondelete="restrict",
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "amenities_categ_id" in vals:
            amenities_categ = self.env["podiatry.device.amenities.type"].browse(
                vals.get("amenities_categ_id")
            )
            vals.update({"categ_id": amenities_categ.product_categ_id.id})
        return super(PodiatryDeviceAmenities, self).create(vals)

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "amenities_categ_id" in vals:
            amenities_categ = self.env["podiatry.device.amenities.type"].browse(
                vals.get("amenities_categ_id")
            )
            vals.update({"categ_id": amenities_categ.product_categ_id.id})
        return super(PodiatryDeviceAmenities, self).write(vals)
