# -*- coding: utf-8 -*-

from . import models
from . import wizard
from . import report

from odoo import api, SUPERUSER_ID

def _create_warehouse_data(env):
    """ This hook is used to add default prescription picking types on every warehouse.
    It is necessary if the prescription module is installed after some warehouses were already created.
    """
    warehouses = env['stock.warehouse'].search([('prescription_type_id', '=', False)])
    for warehouse in warehouses:
        picking_type_vals = warehouse._create_or_update_sequences_and_picking_types()
        if picking_type_vals:
            warehouse.write(picking_type_vals)
