

from odoo import _, api, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    # This is a strategic field used to create an prescription location
    # and prescription operation types in existing warehouses when
    # installing this module.
    prescription = fields.Boolean(
        "Prescription",
        default=True,
        help="Prescription related products can be stored in this warehouse.",
    )
    prescription_in_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Prescription In Type",
    )
    prescription_out_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Prescription Out Type",
    )
    prescription_loc_id = fields.Many2one(
        comodel_name="stock.location",
        string="Prescription Location",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """To create an Prescription location and link it with a new warehouse,
        this method is overridden instead of '_get_locations_values'
        method because the locations that are created with the
        values ​​returned by that method are forced to be children
        of view_location_id, and we don't want that.
        """
        res = super().create(vals_list)
        stock_location = self.env["stock.location"]
        for record in res:
            prescription_location_vals = record._get_prescription_location_values()
            record.prescription_loc_id = stock_location.create(prescription_location_vals).id
        return res

    def _get_prescription_location_values(self):
        """this method is intended to be used by 'create' method
        to create a new Prescription location to be linked to a new warehouse.
        """
        return {
            "name": self.view_location_id.name,
            "active": True,
            "return_location": True,
            "usage": "internal",
            "company_id": self.company_id.id,
            "location_id": self.env.ref("prescription.stock_location_prescription").id,
        }

    def _get_sequence_values(self, name=False, code=False):
        values = super()._get_sequence_values(name=name, code=code)
        values.update(
            {
                "prescription_in_type_id": {
                    "name": self.name + " " + _("Sequence Prescription in"),
                    "prefix": self.code + "/Prescription/IN/",
                    "padding": 5,
                    "company_id": self.company_id.id,
                },
                "prescription_out_type_id": {
                    "name": self.name + " " + _("Sequence Prescription out"),
                    "prefix": self.code + "/Prescription/OUT/",
                    "padding": 5,
                    "company_id": self.company_id.id,
                },
            }
        )
        return values

    def _update_name_and_code(self, new_name=False, new_code=False):
        for warehouse in self:
            sequence_data = warehouse._get_sequence_values()
            warehouse.prescription_in_type_id.sequence_id.write(sequence_data["prescription_in_type_id"])
            warehouse.prescription_out_type_id.sequence_id.write(
                sequence_data["prescription_out_type_id"]
            )

    def _get_picking_type_create_values(self, max_sequence):
        data, next_sequence = super()._get_picking_type_create_values(max_sequence)
        data.update(
            {
                "prescription_in_type_id": {
                    "name": _("Prescription Receipts"),
                    "code": "incoming",
                    "use_create_lots": False,
                    "use_existing_lots": True,
                    "default_location_src_id": False,
                    "default_location_dest_id": self.prescription_loc_id.id,
                    "sequence": max_sequence + 1,
                    "sequence_code": "Prescription/IN",
                    "company_id": self.company_id.id,
                },
                "prescription_out_type_id": {
                    "name": _("Prescription Delivery Orders"),
                    "code": "outgoing",
                    "use_create_lots": False,
                    "use_existing_lots": True,
                    "default_location_src_id": self.prescription_loc_id.id,
                    "default_location_dest_id": False,
                    "sequence": max_sequence + 2,
                    "sequence_code": "Prescription/OUT",
                    "company_id": self.company_id.id,
                },
            }
        )
        return data, max_sequence + 3

    def _get_picking_type_update_values(self):
        data = super()._get_picking_type_update_values()
        data.update(
            {
                "prescription_in_type_id": {"default_location_dest_id": self.prescription_loc_id.id},
                "prescription_out_type_id": {"default_location_src_id": self.prescription_loc_id.id},
            }
        )
        return data

    def _create_or_update_sequences_and_picking_types(self):
        data = super()._create_or_update_sequences_and_picking_types()
        stock_picking_type = self.env["stock.picking.type"]
        if "out_type_id" in data:
            prescription_out_type = stock_picking_type.browse(data["prescription_out_type_id"])
            prescription_out_type.write(
                {"return_picking_type_id": data.get("prescription_in_type_id", False)}
            )
        if "prescription_in_type_id" in data:
            prescription_in_type = stock_picking_type.browse(data["prescription_in_type_id"])
            prescription_in_type.write(
                {"return_picking_type_id": data.get("prescription_out_type_id", False)}
            )
        return data
