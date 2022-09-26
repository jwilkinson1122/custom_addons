# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class PracticeLocation(models.Model):

    _name = "practice.location"
    _description = "Practice Locations"
    _order = "sequence"

    name = fields.Char("Location Name", required=True, index=True)
    sequence = fields.Integer("sequence", default=10)


class PracticePractice(models.Model):

    _name = "practice.practice"
    _description = "Practice Practice"

    product_id = fields.Many2one(
        "product.product",
        "Product_id",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    location_id = fields.Many2one(
        "practice.location",
        "Location No",
        help="At which location the practice is located.",
        ondelete="restrict",
    )
    max_adult = fields.Integer()
    max_child = fields.Integer()
    practice_categ_id = fields.Many2one(
        "practice.practice.type", "Practice Category", required=True, ondelete="restrict"
    )
    practice_devices_ids = fields.Many2many(
        "practice.practice.devices", string="Practice Devices", help="List of practice devices."
    )

    practice_accommodations_ids = fields.Many2many(
        "practice.practice.accommodations", string="Practice Accommodations", help="List of practice accommodations."
    )
    status = fields.Selection(
        [("available", "Available"), ("occupied", "Occupied")],
        default="available",
    )
    capacity = fields.Integer(required=True)
    practice_line_ids = fields.One2many(
        "prescription.practice.line", "practice_id", string="Practice Reservation Line"
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "practice_categ_id" in vals:
            practice_categ = self.env["practice.practice.type"].browse(
                vals.get("practice_categ_id"))
            vals.update({"categ_id": practice_categ.product_categ_id.id})
        return super(PracticePractice, self).create(vals)

    @api.constrains("capacity")
    def _check_capacity(self):
        for practice in self:
            if practice.capacity <= 0:
                raise ValidationError(
                    _("Practice capacity must be more than 0"))

    @api.onchange("ispractice")
    def _ispractice_change(self):
        """
        Based on ispractice, status will be updated.
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
        if "practice_categ_id" in vals:
            practice_categ = self.env["practice.practice.type"].browse(
                vals.get("practice_categ_id"))
            vals.update({"categ_id": practice_categ.product_categ_id.id})
        if "ispractice" in vals and vals["ispractice"] is False:
            vals.update({"color": 2, "status": "occupied"})
        if "ispractice" in vals and vals["ispractice"] is True:
            vals.update({"color": 5, "status": "available"})
        return super(PracticePractice, self).write(vals)

    def set_practice_status_occupied(self):
        """
        This method is used to change the state
        to occupied of the practice practice.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"ispractice": False, "color": 2})

    def set_practice_status_available(self):
        """
        This method is used to change the state
        to available of the practice practice.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"ispractice": True, "color": 5})


class PracticePracticeType(models.Model):

    _name = "practice.practice.type"
    _description = "Practice Type"

    categ_id = fields.Many2one("practice.practice.type", "Category")
    child_ids = fields.One2many(
        "practice.practice.type", "categ_id", "Practice Child Categories")
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
            practice_categ = self.env["practice.practice.type"].browse(
                vals.get("categ_id"))
            vals.update({"parent_id": practice_categ.product_categ_id.id})
        return super(PracticePracticeType, self).create(vals)

    def write(self, vals):
        if "categ_id" in vals:
            practice_categ = self.env["practice.practice.type"].browse(
                vals.get("categ_id"))
            vals.update({"parent_id": practice_categ.product_categ_id.id})
        return super(PracticePracticeType, self).write(vals)

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


class PracticePracticeDevicesType(models.Model):

    _name = "practice.practice.devices.type"
    _description = "devices Type"

    device_id = fields.Many2one(
        "practice.practice.devices.type", "Category")
    child_ids = fields.One2many(
        "practice.practice.devices.type", "device_id", "Devices Child Categories"
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
        if "device_id" in vals:
            device_categ = self.env["practice.practice.devices.type"].browse(
                vals.get("device_id")
            )
            vals.update({"parent_id": device_categ.product_categ_id.id})
        return super(PracticePracticeDevicesType, self).create(vals)

    def write(self, vals):
        if "device_id" in vals:
            device_categ = self.env["practice.practice.devices.type"].browse(
                vals.get("device_id")
            )
            vals.update({"parent_id": device_categ.product_categ_id.id})
        return super(PracticePracticeDevicesType, self).write(vals)

    def name_get(self):
        def get_names(cat):
            """Return the list [cat.name, cat.device_id.name, ...]"""
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.device_id
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
                        [[("device_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("device_id", "in", category_ids)], domain]
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


class PracticePracticeDevices(models.Model):

    _name = "practice.practice.devices"
    _description = "Practice devices"

    product_id = fields.Many2one(
        "product.product",
        "Practice Devices Product",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    devices_categ_id = fields.Many2one(
        "practice.practice.devices.type",
        "Devices Category",
        required=True,
        ondelete="restrict",
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "devices_categ_id" in vals:
            devices_categ = self.env["practice.practice.devices.type"].browse(
                vals.get("devices_categ_id")
            )
            vals.update({"categ_id": devices_categ.product_categ_id.id})
        return super(PracticePracticeDevices, self).create(vals)

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "devices_categ_id" in vals:
            devices_categ = self.env["practice.practice.devices.type"].browse(
                vals.get("devices_categ_id")
            )
            vals.update({"categ_id": devices_categ.product_categ_id.id})
        return super(PracticePracticeDevices, self).write(vals)


class PracticePracticeAccommodationsType(models.Model):

    _name = "practice.practice.accommodations.type"
    _description = "accommodations Type"

    accommodation_id = fields.Many2one(
        "practice.practice.accommodations.type", "Category")
    child_ids = fields.One2many(
        "practice.practice.accommodations.type", "accommodation_id", "Accommodations Child Categories"
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
            accommodation_categ = self.env["practice.practice.accommodations.type"].browse(
                vals.get("accommodation_id")
            )
            vals.update({"parent_id": accommodation_categ.product_categ_id.id})
        return super(PracticePracticeAccommodationsType, self).create(vals)

    def write(self, vals):
        if "accommodation_id" in vals:
            accommodation_categ = self.env["practice.practice.accommodations.type"].browse(
                vals.get("accommodation_id")
            )
            vals.update({"parent_id": accommodation_categ.product_categ_id.id})
        return super(PracticePracticeAccommodationsType, self).write(vals)

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


class PracticePracticeAccommodations(models.Model):

    _name = "practice.practice.accommodations"
    _description = "Practice accommodations"

    product_id = fields.Many2one(
        "product.product",
        "Practice Accommodations Product",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    accommodations_categ_id = fields.Many2one(
        "practice.practice.accommodations.type",
        "Accommodations Category",
        required=True,
        ondelete="restrict",
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "accommodations_categ_id" in vals:
            accommodations_categ = self.env["practice.practice.accommodations.type"].browse(
                vals.get("accommodations_categ_id")
            )
            vals.update({"categ_id": accommodations_categ.product_categ_id.id})
        return super(PracticePracticeAccommodations, self).create(vals)

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "accommodations_categ_id" in vals:
            accommodations_categ = self.env["practice.practice.accommodations.type"].browse(
                vals.get("accommodations_categ_id")
            )
            vals.update({"categ_id": accommodations_categ.product_categ_id.id})
        return super(PracticePracticeAccommodations, self).write(vals)
