# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date


class MergeQuotations(models.TransientModel):
    _name = "merge.quotations"
    _description = "Merge Quotations"

    customer = fields.Many2one("res.partner", string="Customer")
    quotations_date = fields.Date(string="Quotations Date")
    sale_order_line = fields.Many2many("sale.order.line", string="Sale")

    def merge_quotations(self):
        for record in self:
            selected_ids = self.env.context.get("active_ids", [])
            selected_records = self.env["sale.order"].browse(selected_ids)
            self.sale_order_line = selected_records.order_line.ids

            move_line_vals = []
            for lines in self.sale_order_line:
                line = (
                    0,
                    0,
                    {
                        "product_id": lines.product_id.id,
                        "name": lines.name,
                        "product_uom_qty": lines.product_uom_qty,
                        "price_unit": lines.price_unit,
                    },
                )
                move_line_vals.append(line)
            quotation = {
                "partner_id": record.customer.id,
                "date_order": record.quotations_date,
                "order_line": move_line_vals,
            }
            quotation_ids = self.env["sale.order"].create(quotation)

    def merge_andnew(self):
        for record in self:
            selected_ids = self.env.context.get("active_ids", [])
            selected_records = self.env["sale.order"].browse(selected_ids)
            if not self.sale_order_line:
                self.sale_order_line = selected_records.order_line.ids
                move_line_vals = []
                for lines in self.sale_order_line:
                    line = (
                        0,
                        0,
                        {
                            "product_id": lines.product_id.id,
                            "name": lines.name,
                            "product_uom_qty": lines.product_uom_qty,
                            "price_unit": lines.price_unit,
                        },
                    )
                    move_line_vals.append(line)
                quotation = {
                    "partner_id": record.customer.id,
                    "date_order": record.quotations_date,
                    "order_line": move_line_vals,
                }
                quotation_ids = self.env["sale.order"].create(quotation)

            else:
                move_line_vals = []
                for lines in self.sale_order_line:
                    line = (
                        0,
                        0,
                        {
                            "product_id": lines.product_id.id,
                            "name": lines.name,
                            "product_uom_qty": lines.product_uom_qty,
                            "price_unit": lines.price_unit,
                        },
                    )
                    move_line_vals.append(line)
                quotation = {
                    "partner_id": record.customer.id,
                    "date_order": record.quotations_date,
                    "order_line": move_line_vals,
                }
                quotation_ids = self.env["sale.order"].create(quotation)

        return {
            "name": "Merge Quotations",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "merge.quotations",
            "target": "new",
            "context": {
                "default_sale_order_line": self.sale_order_line.ids,
            },
        }

    def merge_andview(self):
        for record in self:
            selected_ids = self.env.context.get("active_ids", [])
            selected_records = self.env["sale.order"].browse(selected_ids)
            self.sale_order_line = selected_records.order_line.ids

            move_line_vals = []
            for lines in self.sale_order_line:
                line = (
                    0,
                    0,
                    {
                        "product_id": lines.product_id.id,
                        "name": lines.name,
                        "product_uom_qty": lines.product_uom_qty,
                        "price_unit": lines.price_unit,
                    },
                )
                move_line_vals.append(line)
            quotation = {
                "partner_id": record.customer.id,
                "date_order": record.quotations_date,
                "order_line": move_line_vals,
            }
            quotation_ids = self.env["sale.order"].create(quotation)
            ir_model_data = self.env["ir.model.data"]
            view_id = ir_model_data._xmlid_lookup("sale.view_order_form")[1]
            record_id = self.env["sale.order"].search(
                [("partner_id", "=", record.customer.id)]
            )

            return {
                "name": record_id.partner_id,
                "view_mode": "form",
                "view_type": "form",
                "views": [(view_id, "form")],
                "view_id": view_id,
                "type": "ir.actions.act_window",
                "res_model": "sale.order",
                "res_id": quotation_ids.id,
            }
