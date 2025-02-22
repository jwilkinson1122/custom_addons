from odoo import fields, models


class EstateOffer(models.Model):
    _name = "estate.offer"
    _description = " Estate Offer"

    amount = fields.Float(string="Amount", required=True)
    buyer_id = fields.Many2one(
        string="Buyer", comodel_name="res.partner", required=True
    )
    date = fields.Date(string="Date", required=True, default=fields.Date.today())
    validity = fields.Integer(
        string="Validity",
        help="The number of days before the offer expires.",
        default=7,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("waiting", "Waiting"),
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        required=True,
        default="waiting",
    )
    property_id = fields.Many2one(
        string="Property", comodel_name="estate.property", required=True
    )
