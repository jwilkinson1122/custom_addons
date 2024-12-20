# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import UserError


class CreatePrescriptionShipment(models.TransientModel):
    _name = "create.prescription.shipment"
    _description = "Create Prescription Shipment"

    def create_prescription_shipment(self):
        active_id = self._context.get("active_id")
        if not active_id:
            raise UserError(_("No prescription selected."))

        prescription = self.env["podiatry.prescription"].browse(active_id)
        if prescription.is_shipped:
            raise UserError(_("This prescription has already been shipped."))

        sale_order = self.env["sale.order"].create(
            {
                "partner_id": prescription.patient_id.patient_id.id,
            }
        )

        if not prescription.prescription_line:
            raise UserError(_("There are no shipment lines to process."))

        for p_line in prescription.prescription_line:
            self.env["sale.order.line"].create(
                {
                    "product_id": p_line.product_id.id,
                    "product_uom": p_line.product_id.uom_id.id,
                    "name": p_line.product_id.name,
                    "product_uom_qty": 1,
                    "price_unit": p_line.product_id.lst_price,
                    "order_id": sale_order.id,
                }
            )

        prescription.write({"is_shipped": True})
        sale_order.action_confirm()
        return sale_order.action_view_delivery()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
