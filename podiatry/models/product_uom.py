from odoo import api, fields, models

class ProductUom(models.Model):
    _inherit = "uom.uom"

    measure_type = fields.Selection(
        string="Type of Measure",
        related="category_id.measure_type",
        store=True,
        readonly=True,
    )

class ProductUomCategory(models.Model):
    _inherit = "uom.category"

    measure_type = fields.Selection(
        string="Type of Measure",
        selection=[
            ("unit", "Units"),
            ("weight", "Weight"),
            ("working_time", "Working Time"),
            ("length", "Length"),
            ("height", "Height"),
            ("surface", "Surface"),
            ("volume", "Volume"),
        ],
        required=True,
    )

    _sql_constraints = [
        (
            "uom_category_unique_type",
            "UNIQUE(measure_type)",
            "You can have only one category per measurement type.",
        ),
    ]


class ProductUoMWithHasCategoryLength(models.Model):
    """Add a boolean to isolate units of measure of category length."""

    _inherit = 'uom.uom'

    has_category_length = fields.Boolean(
        'Has Category Length', compute='_compute_has_category_length', store=True)

    @api.depends('category_id')
    def _compute_has_category_length(self):
        category_length = self.env.ref('uom.uom_categ_length')
        for uom in self:
            uom.has_category_length = uom.category_id == category_length


class ProductUoMWithHasCategoryWeight(models.Model):
    """Add a boolean to isolate units of measure of category weight."""

    _inherit = 'uom.uom'

    has_category_weight = fields.Boolean(
        'Has Category Weight', compute='_compute_has_category_weight', store=True)

    @api.depends('category_id')
    def _compute_has_category_weight(self):
        category_weight = self.env.ref('uom.product_uom_categ_kgm')
        for uom in self:
            uom.has_category_weight = uom.category_id == category_weight
