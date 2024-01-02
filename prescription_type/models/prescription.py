from odoo import api, fields, models


class Prescription(models.Model):
    _inherit = "prescription.order"

    prescription_type_id = fields.Many2one(comodel_name="prescription.type")
    location_id = fields.Many2one(
        compute="_compute_location_id", store=True, readonly=False
    )

    @api.depends("prescription_type_id")
    def _compute_location_id(self):
        res = super()._compute_location_id()
        for rec in self:
            if rec.prescription_type_id.source_location_id:
                rec.location_id = rec.prescription_type_id.source_location_id
        return res


class PrescriptionLine(models.Model):
    _inherit = "prescription.line"

    location_id = fields.Many2one(
        compute="_compute_location_id", store=True, readonly=False
    )
    location_dest_id = fields.Many2one(
        compute="_compute_location_id", store=True, readonly=False
    )

    @api.depends("type", "prescription_id.prescription_type_id")
    def _compute_location_id(self):
        for rec in self:
            if (
                rec.type == "add"
                and rec.prescription_id.prescription_type_id.source_location_add_part_id
            ):
                rec.location_id = (
                    rec.prescription_id.prescription_type_id.source_location_add_part_id
                )
            if (
                rec.type == "add"
                and rec.prescription_id.prescription_type_id.destination_location_add_part_id
            ):
                rec.location_dest_id = (
                    rec.prescription_id.prescription_type_id.destination_location_add_part_id
                )
            if (
                rec.type == "remove"
                and rec.prescription_id.prescription_type_id.source_location_remove_part_id
            ):
                rec.location_id = (
                    rec.prescription_id.prescription_type_id.source_location_remove_part_id
                )
            if (
                rec.type == "remove"
                and rec.prescription_id.prescription_type_id.destination_location_remove_part_id
            ):
                rec.location_dest_id = (
                    rec.prescription_id.prescription_type_id.destination_location_remove_part_id
                )

    @api.onchange("type")
    def onchange_operation_type(self):
        # this onchange was overriding the changes from the compute
        # method `_compute_location_id`, we ensure that the locations
        # in the types have more priority by explicit calling the compute.
        res = super().onchange_operation_type()
        self._compute_location_id()
        return res
