# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    sale_primary_id = fields.Many2one(
        'sale.order',
        compute='_compute_sale_primary_id',
        store=True,
        string="Primary Sale Order",
        index=True,
        auto_join=True,
    )

    @api.depends('group_id.parent_root_id.sale_id')
    def _compute_sale_primary_id(self):
        for rec in self:
            sale = rec.group_id.parent_root_id.sale_id
            if sale:
                rec.sale_primary_id = sale.id

    has_cpq_phantom = fields.Boolean(compute="_compute_has_cpq_phantom", store=True)

    @api.depends("move_ids")
    def _compute_has_cpq_phantom(self):
        for picking_id in self:
            # Check if any move has a Custom BOM
            picking_id.has_cpq_phantom = any(picking_id.move_ids.mapped("cpq_bom_id"))

    cpq_summary_count = fields.Integer(
        string="CPQ Summaries",
        compute="_compute_cpq_summary_count",
        store=False,
    )
    
    @api.depends("move_ids_without_package.sale_line_id")
    def _compute_cpq_summary_count(self):
        for p in self:
            sols = p.move_ids_without_package.mapped("sale_line_id").filtered(
                lambda l: getattr(l.product_template_id, "cpq_ok", False)
            )
            p.cpq_summary_count = len(sols)

    def action_open_cpq_summaries(self):
        self.ensure_one()
        sols = self.move_ids_without_package.mapped("sale_line_id").filtered(
            lambda l: getattr(l.product_template_id, "cpq_ok", False)
        )
        return {
            "type": "ir.actions.act_window",
            "name": "CPQ Summaries",
            "res_model": "sale.order.line",
            "view_mode": "tree,form",
            "domain": [("id", "in", sols.ids)],
            "context": {"search_default_cpq_ok": 1},
        }
        
    # Optional helper if you want a single “primary” MO on the picking
    primary_production_id = fields.Many2one(
        'mrp.production',
        compute='_compute_primary_production',
        store=True,
        index=True,
    )

    cpq_configuration_json = fields.Text(
        string="CPQ Configuration (JSON)",
        compute="_compute_cpq_config",
        store=True,
    )
    
    cpq_configuration_summary = fields.Html(
        string="CPQ Summary",
        sanitize=False,
        compute="_compute_cpq_config",
        store=True,
    )

    @api.depends(
        "move_ids_without_package.production_id",
        "move_ids_without_package.raw_material_production_id",
    )
    def _compute_primary_production(self):
        for p in self:
            mos = (
                p.move_ids_without_package.mapped("production_id")
                | p.move_ids_without_package.mapped("raw_material_production_id")
            )
            p.primary_production_id = mos[:1].id if mos else False

    @api.depends(
        "primary_production_id.cpq_configuration_json",
        "primary_production_id.cpq_configuration_summary",
        "move_ids_without_package.cpq_configuration_json",
        "move_ids_without_package.cpq_configuration_summary",
    )
    def _compute_cpq_config(self):
        for p in self:
            # 1) Prefer the snapshot stored on the MO (single source of truth once produced)
            mo = p.primary_production_id
            if mo and (mo.cpq_configuration_json or mo.cpq_configuration_summary):
                p.cpq_configuration_json = mo.cpq_configuration_json
                p.cpq_configuration_summary = mo.cpq_configuration_summary
                continue

            # 2) Otherwise, fall back to what you pushed onto the stock moves from the SOL
            jsons = [j for j in p.move_ids_without_package.mapped("cpq_configuration_json") if j]
            sums  = [s for s in p.move_ids_without_package.mapped("cpq_configuration_summary") if s]

            # If multiple lines carry CPQ, you can choose to concatenate, or just pick the first.
            p.cpq_configuration_json = jsons[0] if jsons else False
            p.cpq_configuration_summary = sums[0] if sums else False
