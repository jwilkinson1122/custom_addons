# See LICENSE file for full copyright and licensing details.

from . import controllers
from . import models
from . import report
from . import wizard
# from .hooks import post_init_hook


# Import the Environment for creating an environment for superuser
# Import SUPERUSER_ID for using as the user id for the superuser
from odoo.api import Environment, SUPERUSER_ID

def post_init_hook(env):

    def _get_next_picking_type_color():
        """Choose the next available color for the operation types."""
        stock_picking_type = env["stock.picking.type"]
        picking_type = stock_picking_type.search_read(
            [("warehouse_id", "!=", False), ("color", "!=", False)],
            ["color"],
            order="color",
        )
        all_used_colors = [res["color"] for res in picking_type]
        available_colors = [
            color for color in range(0, 12) if color not in all_used_colors
        ]
        return available_colors[0] if available_colors else 0

    def create_prescription_locations(warehouse):
        stock_location = env["stock.location"]
        if not warehouse.prescription_loc_id:
            prescription_location_vals = warehouse._get_prescription_location_values()
            warehouse.prescription_loc_id = (
                stock_location.with_context(active_test=False)
                .create(prescription_location_vals)
                .id
            )

    def create_prescription_picking_types(whs):
        ir_sequence_sudo = env["ir.sequence"].sudo()
        stock_picking_type = env["stock.picking.type"]
        color = _get_next_picking_type_color()
        stock_picking = stock_picking_type.search(
            [("sequence", "!=", False)], limit=1, order="sequence desc"
        )
        max_sequence = stock_picking.sequence or 0
        create_data = whs._get_picking_type_create_values(max_sequence)[0]
        sequence_data = whs._get_sequence_values()
        data = {}
        for picking_type, values in create_data.items():
            if (
                picking_type in ["prescription_in_type_id", "prescription_out_type_id"]
                and not whs[picking_type]
            ):
                picking_sequence = sequence_data[picking_type]
                sequence = ir_sequence_sudo.create(picking_sequence)
                values.update(
                    warehouse_id=whs.id,
                    color=color,
                    sequence_id=sequence.id,
                )
                data[picking_type] = stock_picking_type.create(values).id

        if data:
            whs.write(data)
        whs.prescription_in_type_id.return_picking_type_id = whs.prescription_out_type_id.id
        whs.prescription_out_type_id.return_picking_type_id = whs.prescription_in_type_id.id

    # Create prescription locations and picking types
    warehouses = env["stock.warehouse"].search([])
    for warehouse in warehouses:
        create_prescription_locations(warehouse)
        create_prescription_picking_types(warehouse)
    # Create prescription sequence per company
    for company in env["res.company"].search([]):
        company.create_prescription_index()
