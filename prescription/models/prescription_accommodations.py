# See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.osv import expression


class PrescriptionAccommodations(models.Model):

    _name = "prescription.accommodations"
    _description = "Prescription Accommodations and its charges"

    product_id = fields.Many2one(
        "product.product",
        "Accommodation_id",
        required=True,
        ondelete="cascade",
        delegate=True,
    )
    accommodation_categ_id = fields.Many2one(
        "prescription.accommodation.type",
        "Accommodation Category",
        required=True,
        ondelete="restrict",
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "accommodation_categ_id" in vals:
            accommodation_categ = self.env["prescription.accommodation.type"].browse(
                vals.get("accommodation_categ_id")
            )
            vals.update({"categ_id": accommodation_categ.product_categ_id.id})
        return super(PrescriptionAccommodations, self).create(vals)

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "accommodation_categ_id" in vals:
            accommodation_categ_id = self.env["prescription.accommodation.type"].browse(
                vals.get("accommodation_categ_id")
            )
            vals.update({"categ_id": accommodation_categ_id.product_categ_id.id})
        return super(PrescriptionAccommodations, self).write(vals)


class PrescriptionAccommodationType(models.Model):

    _name = "prescription.accommodation.type"
    _description = "Accommodation Type"

    accommodation_id = fields.Many2one("prescription.accommodation.type", "Accommodation Category")
    child_ids = fields.One2many(
        "prescription.accommodation.type", "accommodation_id", "Accommodation Child Categories"
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
            accommodation_categ = self.env["prescription.accommodation.type"].browse(
                vals.get("accommodation_id")
            )
            vals.update({"parent_id": accommodation_categ.product_categ_id.id})
        return super(PrescriptionAccommodationType, self).create(vals)

    def write(self, vals):
        if "accommodation_id" in vals:
            accommodation_categ = self.env["prescription.accommodation.type"].browse(
                vals.get("accommodation_id")
            )
            vals.update({"parent_id": accommodation_categ.product_categ_id.id})
        return super(PrescriptionAccommodationType, self).write(vals)

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
