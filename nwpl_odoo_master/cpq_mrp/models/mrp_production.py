# -*- coding: utf-8 -*-
import logging
import base64
from io import BytesIO

import qrcode

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # ----------------------------
    # Links to the originating sale
    # ----------------------------
    ptav_ids = fields.Many2many(
        'product.template.attribute.value',
        'mrp_production_ptav_rel',
        'production_id', 'ptav_id',
        string="Selected PTAVs"
    )
    
    sale_line_id = fields.Many2one(
        "sale.order.line",
        string="Source SOL",
        compute="_compute_sale_line_id",
        store=True,
        index=True,
        help="Resolved from the finished move(s) that carry a sale line.",
    )

    sale_primary_id = fields.Many2one(
        "sale.order",
        compute="_compute_sale_primary_id",
        store=True,
        string="Primary Sale Order",
        index=True,
        auto_join=True,
        help="Root sale order inferred from the procurement chain.",
    )
    
    repair_id = fields.Many2one("repair.order")

    partner_id = fields.Many2one(
        related="sale_primary_id.partner_id",
        readonly=True,
        string="Customer",
        store=True,
    )
    commitment_date = fields.Datetime(
        related="sale_primary_id.commitment_date",
        string="Commitment Date",
        store=True,
        readonly=True,
    )
    client_order_ref = fields.Char(
        related="sale_primary_id.client_order_ref",
        string="Customer Reference",
        store=True,
        readonly=True,
    )

    # ----------------------------
    # CPQ snapshot (stored on MO)
    # Auto-synced whenever the linked SOL changes
    # ----------------------------
    cpq_configuration_json = fields.Text(
        "CPQ Configuration (JSON)",
        compute="_compute_cpq_snapshot",
        store=True,
    )
    cpq_configuration_summary = fields.Html(
        "CPQ Summary",
        sanitize=False,
        compute="_compute_cpq_snapshot",
        store=True,
    )
    cpq_config_hash = fields.Char(
        "CPQ Config Hash",
        compute="_compute_cpq_snapshot",
        store=True,
    )

    # QR image derived from the hash + ids
    cpq_qr_code_image = fields.Binary(
        string="QR Code",
        compute="_compute_cpq_qr_code_image",
        store=True,
    )

    cpq_label_qty = fields.Integer(
        string="Label Quantity",
        default=1,
        help="Number of labels to print for this MO (e.g., for QR labels).",
    )
    
    cpq_dynamic_bom_id = fields.Many2one('cpq.dynamic.bom', readonly=True)
    # cpq_selected_ptav_ids = fields.Many2many('product.template.attribute.value', readonly=True)
    cpq_selected_ptav_ids = fields.Many2many(
        'product.template.attribute.value',
        'mrp_production_cpq_selected_ptav_rel', 
        'production_id',                        
        'ptav_id',                              
        string="Selected PTAVs",
        readonly=True,
        help="PTAVs resolved from the CPQ config used to build this MO.",
    )
    cpq_custom_map = fields.Json(readonly=True)
    cpq_laterality = fields.Selection([('left','Left'),('right','Right'),('bilateral','Bilateral')], readonly=True)


    # ---------- COMPUTES ----------

    @api.depends("move_finished_ids", "move_finished_ids.sale_line_id")
    def _compute_sale_line_id(self):
        """
        Prefer a finished move tied to a SOL (typical sale->manufacture flow).
        We take the first finished move that has a sale_line_id.
        """
        for mo in self:
            move = mo.move_finished_ids.filtered("sale_line_id")[:1]
            mo.sale_line_id = move.sale_line_id.id if move else False


    @api.depends('procurement_group_id.parent_root_id.sale_id')
    def _compute_sale_primary_id(self):
        for rec in self:
            sale = rec.procurement_group_id.parent_root_id.sale_id
            if sale:
                rec.sale_primary_id = sale.id

    @api.depends(
        "sale_line_id",
        "sale_line_id.product_template_id.cpq_ok",
        "sale_line_id.cpq_configuration_json",
        "sale_line_id.cpq_configuration_summary",
        "sale_line_id.cpq_config_hash",
    )
    def _compute_cpq_snapshot(self):
        """
        Keep a stored snapshot on the MO so the shop floor can see
        the exact configuration even if the SOL later changes.
        """
        for mo in self:
            sol = mo.sale_line_id
            if sol and getattr(sol.product_template_id, "cpq_ok", False):
                mo.cpq_configuration_json = sol.cpq_configuration_json or False
                mo.cpq_configuration_summary = sol.cpq_configuration_summary or False
                mo.cpq_config_hash = sol.cpq_config_hash or False
            else:
                mo.cpq_configuration_json = False
                mo.cpq_configuration_summary = False
                mo.cpq_config_hash = False

    @api.depends(
        "cpq_config_hash",
        "sale_line_id",
        "sale_line_id.order_id",
        "sale_line_id.product_template_id",
        "cpq_configuration_json",
    )
    def _compute_cpq_qr_code_image(self):
        """
        Generate a small PNG QR code from a canonical payload when we have
        enough information (order, line, template, config hash).
        """
        for mo in self:
            try:
                sol = mo.sale_line_id
                if not (sol and mo.cpq_config_hash and sol.order_id and sol.product_template_id):
                    mo.cpq_qr_code_image = False
                    continue

                payload = (
                    f"cpq://order/{sol.order_id.id}"
                    f"/line/{sol.id}"
                    f"/template/{sol.product_template_id.id}"
                    f"?config={mo.cpq_config_hash}"
                )

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=3,
                    border=4,
                )
                qr.add_data(payload)
                qr.make(fit=True)
                img = qr.make_image()
                buf = BytesIO()
                img.save(buf, format="PNG")
                mo.cpq_qr_code_image = base64.b64encode(buf.getvalue())
            except Exception as e:
                _logger.warning("Failed to generate CPQ QR for MO %s: %s", mo.name, e)
                mo.cpq_qr_code_image = False

    # ---------- ACTIONS / HELPERS ----------
    
    def _bom_explode(self, bom, product, quantity):
        """
        Pass CPQ ptav_ids into context for dynamic BOM matching logic.
        """
        # In case ptav_ids field is defined and populated
        ctx = dict(self.env.context)
        if self.ptav_ids:
            ctx["cpq_ptav_ids"] = self.ptav_ids.ids
        return super(MrpProduction, self.with_context(ctx))._bom_explode(bom, product, quantity)

    def action_refresh_cpq_from_sale(self):
        """
        Manual 'refresh' in case someone wants to force a recompute.
        Touching sale_line_id will schedule the compute.
        """
        for mo in self:
            mo.sale_line_id = mo.sale_line_id  # no-op write to trigger recompute
        return True

    def action_return_to_draft(self):
        self._check_company()
        for rec in self:
            if rec.state not in ("confirmed", "cancel"):
                raise UserError(
                    _(
                        "You cannot return to draft the following MO: %s. "
                        "Only confirmed or cancelled MO can be returned to draft."
                    )
                    % rec.name
                )
            (rec.move_raw_ids + rec.move_finished_ids)._action_cancel()
            (rec.move_raw_ids + rec.move_finished_ids).write({"state": "draft"})
            rec.workorder_ids.write({"state": "waiting"})
            if rec.state != "draft":
                raise UserError(_("Could not set the production order back to draft"))

    @api.depends("move_raw_ids.state", "move_finished_ids.state")
    def _compute_state(self):
        super()._compute_state()
        for production in self:
            if (
                production.state == "cancel"
                and all(m.state == "draft" for m in production.move_raw_ids)
                and all(m.state == "draft" for m in production.move_finished_ids)
            ):
                production.state = "draft"

    @api.model
    def create(self, vals):
        # copy CPQ values if stock.rule provided them
        for k in ('cpq_dynamic_bom_id', 'cpq_custom_map', 'cpq_laterality'):
            if k in self.env.context and k not in vals:
                vals[k] = self.env.context[k]
        return super().create(vals)

    # In Odoo 17, `_get_moves_raw_values` is the hook building component moves.
    def _get_moves_raw_values(self):
        self.ensure_one()
        # If we have a CPQ Dynamic BoM, generate components from it
        if self.cpq_dynamic_bom_id:
            # Make sure the product we're manufacturing matches the Dynamic BoM's template
            if self.product_id.product_tmpl_id != self.cpq_dynamic_bom_id.product_tmpl_id:
                return super()._get_moves_raw_values()

            # Use your existing explode
            exploded = self.cpq_dynamic_bom_id.explode(self.product_id, self.product_qty)
            lines = []
            for product, qty, uom, _line in exploded:
                # Build a normal components move line dict (minimal fields)
                lines.append({
                    'name': product.display_name,
                    'date': self.date_planned_start,
                    'date_deadline': self.date_deadline,
                    'bom_line_id': False,  # dynamic
                    'product_id': product.id,
                    'product_uom': uom.id,
                    'product_uom_qty': qty,
                    'location_id': self.location_src_id.id,
                    'location_dest_id': self.product_id.with_company(self.company_id).property_stock_production.id,
                    'company_id': self.company_id.id,
                    'operation_id': False,
                    'warehouse_id': self._get_warehouse().id if hasattr(self, '_get_warehouse') else False,
                    'procure_method': 'make_to_stock',
                    'state': 'draft',
                })
            return lines

        # Fallback: standard behavior
        return super()._get_moves_raw_values()

    def action_create_repair_order(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("repair.action_repair_order_form")
        action["view_mode"] = "form"
        action["views"] = [(False, "form")]
        action["target"] = "new"
        action["name"] = _("Create Repair Order")

        action["context"] = {
            "default_product_id": self.product_id.id,
            "default_product_qty": self.product_qty,
            "default_mrp_ids": [self.id],
        }
        return action

    def action_view_mrp_production_repair_orders(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "repair.order",
            "res_id": self.repair_id.id,
        }

    def action_confirm(self):
        res = super().action_confirm()
        for bom_line in self.bom_id.bom_line_ids:
            if bom_line.component_template_id:
                # product_id was set in mrp.bom.explode for correct flow.
                # Need to remove it.
                bom_line.product_id = False
        return res

    @api.constrains("bom_id")
    def _check_component_attributes(self):
        self.bom_id._check_component_attributes()
        
    def _generate_workorders(self):
        res = super()._generate_workorders()

        for mo in self:
            ptavs = mo.ptav_ids
            summary = mo.cpq_configuration_summary

            for wo in mo.workorder_ids:
                wo.ptav_ids = [(6, 0, ptavs.ids)]
                wo.cpq_configuration_summary = summary
        _logger.info("Injected %s ptavs into workorder %s", len(ptavs), wo.name)

        return res