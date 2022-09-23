# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class PracticeLocation(models.Model):

    _name = "practice.location"
    _description = "Location"
    _order = "sequence"

    name = fields.Char("Location Name", required=True, index=True)
    sequence = fields.Integer("sequence", default=10)


class PracticeRoom(models.Model):

    _name = "practice.practice"
    _description = "Practice Room"

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
        "practice.practice.type", "Room Category", required=True, ondelete="restrict"
    )
    practice_amenities_ids = fields.Many2many(
        "practice.practice.amenities", string="Room Amenities", help="List of practice amenities."
    )
    status = fields.Selection(
        [("available", "Available"), ("occupied", "Occupied")],
        default="available",
    )
    capacity = fields.Integer(required=True)
    practice_line_ids = fields.One2many(
        "prescription.practice.line", "practice_id", string="Room Reservation Line"
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "practice_categ_id" in vals:
            practice_categ = self.env["practice.practice.type"].browse(
                vals.get("practice_categ_id"))
            vals.update({"categ_id": practice_categ.product_categ_id.id})
        return super(PracticeRoom, self).create(vals)

    @api.constrains("capacity")
    def _check_capacity(self):
        for practice in self:
            if practice.capacity <= 0:
                raise ValidationError(_("Room capacity must be more than 0"))

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
        return super(PracticeRoom, self).write(vals)

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


class PracticeRoomType(models.Model):

    _name = "practice.practice.type"
    _description = "Room Type"

    categ_id = fields.Many2one("practice.practice.type", "Category")
    child_ids = fields.One2many(
        "practice.practice.type", "categ_id", "Room Child Categories")
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
        return super(PracticeRoomType, self).create(vals)

    def write(self, vals):
        if "categ_id" in vals:
            practice_categ = self.env["practice.practice.type"].browse(
                vals.get("categ_id"))
            vals.update({"parent_id": practice_categ.product_categ_id.id})
        return super(PracticeRoomType, self).write(vals)

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


class PracticeRoomAmenitiesType(models.Model):

    _name = "practice.practice.amenities.type"
    _description = "amenities Type"

    amenity_id = fields.Many2one(
        "practice.practice.amenities.type", "Category")
    child_ids = fields.One2many(
        "practice.practice.amenities.type", "amenity_id", "Amenities Child Categories"
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
            amenity_categ = self.env["practice.practice.amenities.type"].browse(
                vals.get("amenity_id")
            )
            vals.update({"parent_id": amenity_categ.product_categ_id.id})
        return super(PracticeRoomAmenitiesType, self).create(vals)

    def write(self, vals):
        if "amenity_id" in vals:
            amenity_categ = self.env["practice.practice.amenities.type"].browse(
                vals.get("amenity_id")
            )
            vals.update({"parent_id": amenity_categ.product_categ_id.id})
        return super(PracticeRoomAmenitiesType, self).write(vals)

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


class PracticeRoomAmenities(models.Model):

    _name = "practice.practice.amenities"
    _description = "Room amenities"

    product_id = fields.Many2one(
        "product.product",
        "Room Amenities Product",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    amenities_categ_id = fields.Many2one(
        "practice.practice.amenities.type",
        "Amenities Category",
        required=True,
        ondelete="restrict",
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "amenities_categ_id" in vals:
            amenities_categ = self.env["practice.practice.amenities.type"].browse(
                vals.get("amenities_categ_id")
            )
            vals.update({"categ_id": amenities_categ.product_categ_id.id})
        return super(PracticeRoomAmenities, self).create(vals)

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "amenities_categ_id" in vals:
            amenities_categ = self.env["practice.practice.amenities.type"].browse(
                vals.get("amenities_categ_id")
            )
            vals.update({"categ_id": amenities_categ.product_categ_id.id})
        return super(PracticeRoomAmenities, self).write(vals)
