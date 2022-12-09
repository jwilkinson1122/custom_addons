from odoo import models, fields


class ShoeSize(models.Model):
    _name = 'podiatry.patient.shoe_size'
    _description = "Shoe Size"
    _order = 'sequence,id'

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Shoe Size",
        # required=True,
        index=True, translate=True,
    )

    mens = fields.Char(
        string="Men / Youth",
        required=True,
        index=True, translate=True,
    )

    womens = fields.Char(
        string="Women's",
        # required=True,
        index=True, translate=True,
    )

    uk = fields.Char(
        string="UK",
        # required=True,
        index=True, translate=True,
    )

    euro = fields.Char(
        string="Euro",
        # required=True,
        index=True, translate=True,
    )

    # childrens = fields.Char(
    #     string="Child Size",
    #     required=True,
    #     index=True, translate=True,
    # )

    code = fields.Char(
        string="Code",
        copy=False,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=5,
    )

    notes = fields.Text(
        string="Notes",
    )
