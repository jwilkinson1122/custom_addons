# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import UserError


class CreatePrescriptionInvoice(models.TransientModel):
    _name = "create.prescription.invoice"
    _description = "Create Prescription Invoice"

    def create_prescription_invoice(self):
        active_ids = self._context.get("active_ids", [])
        if not active_ids:
            raise UserError(_("No prescriptions selected."))

        lab_req_obj = self.env["podiatry.prescription"]
        lab_reqs = lab_req_obj.browse(active_ids)

        inv_list = []
        for lab_req in lab_reqs:
            if not lab_req.prescription_line:
                raise UserError(_("At least one prescription line is required."))

            if lab_req.is_invoiced:
                raise UserError(_("This prescription has already been invoiced."))

            sale_journals = self.env["account.journal"].search([("type", "=", "sale")])
            invoice_vals = {
                "name": self.env["ir.sequence"].next_by_code("pres_inv_seq"),
                "invoice_origin": lab_req.name or "",
                "move_type": "out_invoice",
                "partner_id": lab_req.patient_id.patient_id.id,
                "invoice_date": date.today(),
                "partner_shipping_id": lab_req.patient_id.patient_id.id,
                "currency_id": lab_req.patient_id.patient_id.currency_id.id,
                "fiscal_position_id": lab_req.patient_id.patient_id.property_account_position_id.id,
                "company_id": lab_req.patient_id.patient_id.company_id.id or False,
            }

            invoice = self.env["account.move"].create(invoice_vals)
            invoice_lines = []

            for p_line in lab_req.prescription_line:
                account_id = (
                    p_line.product_id.property_account_income_id.id
                    or p_line.product_id.categ_id.property_account_income_categ_id.id
                )
                if not account_id:
                    account_id = self.env["ir.property"].get(
                        "property_account_income_categ_id", "product.category"
                    )
                if not account_id:
                    raise UserError(
                        _(
                            'No income account defined for product "%s". Please configure a chart of accounts.'
                        )
                        % (p_line.product_id.name,)
                    )

                taxes = p_line.product_id.taxes_id.filtered(
                    lambda tax: not p_line.product_id.company_id
                    or tax.company_id == p_line.product_id.company_id
                )

                invoice_lines.append(
                    (
                        0,
                        0,
                        {
                            "name": p_line.product_id.display_name or "",
                            "account_id": account_id,
                            "price_unit": p_line.product_id.lst_price,
                            "product_uom_id": p_line.product_id.uom_id.id,
                            "quantity": 1,
                            "product_id": p_line.product_id.id,
                            "tax_ids": [(6, 0, taxes.ids)],
                        },
                    )
                )

            invoice.write({"invoice_line_ids": invoice_lines})
            lab_req.write({"is_invoiced": True})
            inv_list.append(invoice.id)

        if inv_list:
            action = self.env.ref("account.action_move_out_invoice_type")
            return {
                "name": action.name,
                "type": action.type,
                "views": [
                    (self.env.ref("account.view_invoice_tree").id, "tree"),
                    (self.env.ref("account.view_move_form").id, "form"),
                ],
                "target": action.target,
                "context": action.context,
                "res_model": action.res_model,
                "domain": [("id", "in", inv_list)],
            }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
