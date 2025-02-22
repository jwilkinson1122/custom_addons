from odoo import fields, models, api
from odoo.tools import date_utils
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import ValidationError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate properties"

    name = fields.Char(required=True)
    description = fields.Text()
    image = fields.Image(string="image")
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        string="State",
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("under_option", "Under Option"),
            ("sold", "Sold"),
        ],
        required=True,
        default="new",
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="estate.property.type",
        ondelete="restrict",
        required=True,
    )
    postcode = fields.Char()

    # Prices
    expected_price = fields.Float(required=True)

    best_offer = fields.Float(
        copy=False,
        string="Best offer",
        help="The Best offer excluding taxes.",
        readonly=True,
        default=0.00,
        compute="_compute_best_offer",
        required=True,
    )
    selling_price = fields.Float(
        copy=False,
        string="Selling Price",
        help="The selling price excluding taxes.",
        default=0.00,
        required=True,
    )

    _sql_constraints = [
        (
            "check_expected_prices",
            "CHECK(expected_price >= 0)",
            "The expected price should be greater or equals to 0.",
        ),
        (
            "check_selling_prices",
            "CHECK(selling_price >= 0)",
            "The selling price should be greater or equals to 0.",
        ),
    ]

    availability_date = fields.Date(
        copy=False,
        string="Availability Date",
        default=date_utils.add(fields.Date.today(), months=2),
    )
    floor_area = fields.Integer(
        string="Floor Area",
        help="The floor area in square meters excluding the garden.",
    )
    bedrooms = fields.Integer(string="Number of Bedrooms", default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    has_garage = fields.Boolean()
    has_garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [("north", "North"), ("south", "South"), ("west", "West"), ("east", "East")]
    )
    seller_id = fields.Many2one(
        string="Seller", comodel_name="res.partner", required=True
    )
    salesperson_id = fields.Many2one(string="Salesperson", comodel_name="res.users")

    offer_ids = fields.One2many(
        string="Offers", comodel_name="estate.offer", inverse_name="property_id"
    )
    tag_ids = fields.Many2many(string="Tags", comodel_name="estate.tag")

    @api.depends("expected_price")
    def _compute_best_offer(self):
        print(f"INFO: records to compute", self)
        for record in self:
            record.best_offer = record.expected_price

    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if record.selling_price == 0:
                continue

            diff = float_round(
                record.expected_price - record.selling_price,
                precision_rounding=2,
            )

            ten_percent_of_expected_price = float_round(
                record.expected_price * 0.1,
                precision_rounding=2,
            )

            diff_float_compared = float_compare(
                diff, ten_percent_of_expected_price, precision_rounding=2
            )

            print(f"INFO: ", diff, ten_percent_of_expected_price, diff_float_compared)

            if diff_float_compared > 0:
                raise ValidationError(
                    "selling price need to be at least 90 percent of expected price"
                )
