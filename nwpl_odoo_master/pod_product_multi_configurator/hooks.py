import base64
import ast
import os
from pathlib import Path
import logging
import requests
from odoo import api, fields, models, SUPERUSER_ID
from odoo.modules.module import get_module_resource
from odoo.tools.sql import column_exists, create_column
from odoo.tools import file_open


_logger = logging.getLogger(__name__)

def post_init_hook(env):
    UoM = env["uom.uom"]
    UoMCateg = env["uom.category"]

    # Find the standard Unit(s) category (fallback by name if xmlid missing)
    categ = env.ref("uom.product_uom_categ_unit", raise_if_not_found=False) \
            or UoMCateg.search([("name", "ilike", "Unit")], limit=1)

    if not categ:
        return  # extremely unlikely, but don’t crash

    # Look for an existing “Pairs” in that category with factor_inv=2 and bigger type
    existing = UoM.search([
        ("category_id", "=", categ.id),
        ("uom_type", "=", "bigger"),
        ("factor_inv", "=", 2.0),
        ("name", "ilike", "pair"),
    ], limit=1)

    if not existing:
        UoM.create({
            "name": "Pair(s)",
            "category_id": categ.id,
            "uom_type": "bigger",
            "factor_inv": 2.0,
            "rounding": 1.0,
            "active": True,
        })
