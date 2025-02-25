# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartnerContactDepartment(models.Model):
    _name = "res.partner.contact.department"
    _order = "parent_path"
    _parent_order = "name"
    _parent_store = True
    _description = "Department"

    name = fields.Char(required=True, translate=True)
    parent_id = fields.Many2one(
        "res.partner.contact.department", "Parent department", ondelete="restrict"
    )
    child_ids = fields.One2many(
        "res.partner.contact.department", "parent_id", "Child departments"
    )
    parent_path = fields.Char(index=True, unaccent=False)
