# -*- coding: utf-8 -*-
import logging
from odoo import SUPERUSER_ID, _, api, fields, models
# from pod_flexible_bom.models import production

_logger = logging.getLogger(__name__)

class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    mrp_production_ids = fields.One2many("mrp.production", "procurement_group_id")
    
    parent_root_id = fields.Many2one(
        'procurement.group',
        compute='_compute_parent_root_id',
        store=True,
        recursive=True,
    )

    @api.depends('stock_move_ids.move_dest_ids.group_id')
    def _compute_parent_root_id(self):
        for rec in self:
            rec.parent_root_id = rec._get_parent_root()

    def _get_parent_root(self):
        def get_parent(g):
            groups = g.stock_move_ids.move_dest_ids.group_id
            # Parent is the one the was created before every other procurement
            # group! We do this to avoid infinite looping where going from
            # related dest moves to other group can lead to self group back
            # and forth!
            parent = min(groups, key=lambda x: x.id, default=g.browse())
            # Exclude itself to avoid infinite loop!
            return parent - g

        self.ensure_one()
        parent_group = self
        candidate = get_parent(parent_group)
        while candidate:
            parent_group = candidate
            candidate = get_parent(parent_group)
        return parent_group


    @api.model
    def run(self, procurements, raise_user_error=True):
        """
        If 'run' is called on a kit which is a cpq_ok item we need to
        ensure that any BoM already exists, or is created before anything else
        in the procurement system runs. This is most critical for kits.

        We don't just override _bom_find because Odoo will call _bom_find in
        many many other places, and we dont want it creating a BoM, or any
        dynamic children unnecessarily.
        """
        procurements_without_dynamic_kit = []

        for procurement in procurements:
            product_id = procurement.product_id.with_company(procurement.company_id)
            should_explode = (
                product_id.cpq_ok and product_id.cpq_dynamic_bom_ids.type == "phantom"
            )
            if should_explode:
                bom_kit = product_id.cpq_dynamic_bom_ids
                order_qty = procurement.product_uom._compute_quantity(
                    procurement.product_qty, bom_kit.product_uom_id, round=False
                )
                qty_to_produce = order_qty / bom_kit.product_qty

                bom_lines = product_id.cpq_dynamic_bom_ids.explode(
                    product_id, qty_to_produce
                )

                for (
                    idx,
                    (
                        dyn_bom_product_id,
                        dyn_bom_product_qty,
                        dyn_uom_id,
                        cpq_bom_line_id,
                    ),
                ) in enumerate(bom_lines):
                    values = dict(**procurement.values)
                    values.update(
                        {
                            "cpq_bom_id": bom_kit.id,
                            "cpq_bom_line_id": cpq_bom_line_id.id,
                            "cpq_description": f"{product_id.display_name} - \
                                {idx + 1}/{len(bom_lines)}",
                        }
                    )
                    procurements_without_dynamic_kit.append(
                        self.env["procurement.group"].Procurement(
                            dyn_bom_product_id,
                            dyn_bom_product_qty,
                            dyn_uom_id,
                            procurement.location_id,
                            procurement.name,
                            procurement.origin,
                            procurement.company_id,
                            values,
                        )
                    )
            else:
                procurements_without_dynamic_kit.append(procurement)

        return super().run(
            procurements_without_dynamic_kit, raise_user_error=raise_user_error
        )

CPQ_WRAPPER_CODE = '__CPQ_WRAPPER__'

class StockRule(models.Model):
    _inherit = "stock.rule"

    # -----------------------------
    # Helpers
    # -----------------------------
    def _ensure_record(self, model, rec_or_id):
        """Return a recordset from either an ID or a record (or False)."""
        if not rec_or_id:
            return self.env[model]
        if hasattr(rec_or_id, "_name"):
            return rec_or_id
        return self.env[model].browse(rec_or_id)
    
    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom):
        vals = super()._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom)
        sol_id = values.get('sale_line_id')
        if sol_id:
            vals['sale_line_id'] = sol_id
        # Copy CPQ context too so it's on the MO record
        for key in ('cpq_dynamic_bom_id', 'cpq_custom_map', 'cpq_laterality'):
            if key in values:
                vals[key] = values[key]
        if 'cpq_selected_ptav_ids' in values:
            vals['cpq_selected_ptav_ids'] = values['cpq_selected_ptav_ids']
        return vals

    def _copy_cpq_from_sol_into_move_vals(self, move_vals, sol):
        """Copy CPQ fields from a Sale Order Line into a dict of stock.move vals."""
        if not sol:
            return move_vals
        if getattr(sol.product_template_id, "cpq_ok", False):
            # Only include keys that actually have values to avoid noise
            if sol.cpq_configuration_json:
                move_vals["cpq_configuration_json"] = sol.cpq_configuration_json
            if sol.cpq_configuration_summary:
                move_vals["cpq_configuration_summary"] = sol.cpq_configuration_summary
            if getattr(sol, "cpq_config_hash", False):
                move_vals["cpq_config_hash"] = sol.cpq_config_hash
            if getattr(sol, "cpq_qr_code_image", False):
                move_vals["cpq_qr_code_image"] = sol.cpq_qr_code_image
        return move_vals

    def _attach_sol_and_cpq_to_finished_moves(self, production, sol):
        """
        Once the MO is confirmed and finished moves exist, link them to SOL and
        copy the CPQ payload onto the finished moves.
        """
        if not production or not production.exists() or not sol:
            return

        for mv in production.move_finished_ids:
            # Link SOL (so later mrp.production.sale_line_id compute will find it)
            if not mv.sale_line_id:
                mv.sale_line_id = sol.id
            # Copy CPQ fields for traceability on the finished product move
            vals = {}
            self._copy_cpq_from_sol_into_move_vals(vals, sol)
            if vals:
                mv.write(vals)

    # -----------------------------
    # Pull rules: pass CPQ to stock.move
    # -----------------------------
    def _get_matching_bom(self, product_id, company_id, values):
        """Try normal BoM first; if none, fall back to CPQ Dynamic BoM wrapper."""
        bom = super()._get_matching_bom(product_id, company_id, values)
        if bom:
            return bom

        sol = self.env['sale.order.line'].browse(values.get('sale_line_id') or False)
        if not sol or not sol.cpq_dynamic_bom_id or sol.cpq_dynamic_bom_id.type != 'normal':
            return bom  # keep None

        dyn = sol.cpq_dynamic_bom_id.sudo()
        template = product_id.product_tmpl_id

        # Create/reuse a tiny wrapper BoM once per (template, picking_type)
        wrapper = self.env['mrp.bom'].sudo().search([
            ('product_tmpl_id', '=', template.id),
            ('code', '=', CPQ_WRAPPER_CODE),
            ('type', '=', 'normal'),
            ('picking_type_id', '=', dyn.picking_type_id.id),
            ('company_id', '=', dyn.company_id.id),
        ], limit=1)
        if not wrapper:
            wrapper = self.env['mrp.bom'].sudo().create({
                'product_tmpl_id': template.id,
                'type': 'normal',
                'picking_type_id': dyn.picking_type_id.id,
                'company_id': dyn.company_id.id,
                'product_uom_id': template.uom_id.id,
                'code': CPQ_WRAPPER_CODE,
            })

        # Make sure the downstream MO has the CPQ context to explode correctly
        values.update({
            'cpq_dynamic_bom_id': dyn.id,
            'cpq_selected_ptav_ids': [ (6, 0, sol.cpq_selected_ptav_ids.ids) ],
            'cpq_custom_map': sol.cpq_custom_map or {},
            'cpq_laterality': sol.cpq_laterality or False,
        })
        return wrapper
    
    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        move_values = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )

        # Normalize SOL (can be id or record)
        sol = self._ensure_record("sale.order.line", values.get("sale_line_id"))
        if sol:
            move_values = self._copy_cpq_from_sol_into_move_vals(move_values, sol)

        # Extra CPQ metadata (when exploding a CPQ-driven BoM into component moves)
        for key in ("cpq_bom_line_id", "cpq_bom_id", "cpq_description"):
            if key in values and values[key]:
                move_values[key] = values[key]

        return move_values

    # -----------------------------
    # Manufacture: create MO, raw & finished moves, then link SOL + CPQ to finished moves
    # -----------------------------
    @api.model
    def _run_manufacture(self, procurements):
        """Create/confirm the MO, then attach sale_line_id & CPQ snapshot to FINISHED moves."""
        remaining = []

        for procurement, rule in procurements:
            product = procurement.product_id.with_company(procurement.company_id)

            # Only intercept CPQ "normal" BoMs you want to manufacture here
            if product.cpq_ok and product.cpq_dynamic_bom_ids.type == "normal":
                sol = procurement.values.get("sale_line_id")
                if sol and not getattr(sol, "_name", False):
                    sol = self.env["sale.order.line"].browse(sol)

                # ensure we have a BoM
                bom = product.cpq_dynamic_bom_ids
                company = procurement.company_id

                # Build base production values the Odoo way
                production_vals = rule._prepare_mo_vals(*procurement, self.env["mrp.bom"])
                production_vals.update({
                    'bom_id': bom.id,                     
                    'consumption': bom.consumption or 'flexible',
                    'picking_type_id': bom.picking_type_id.id or procurement.rule_id.picking_type_id.id,
                })

                # Create the MO as superuser (matches Odoo core behavior)
                production = (
                    self.env["mrp.production"]
                    .with_user(SUPERUSER_ID)
                    .sudo()
                    .with_company(company)
                    .create(production_vals)
                )

                # Let Odoo create its own moves (raw + finished)
                # This avoids double-creating moves
                production.action_confirm()

                # ---- Attach Sale Line & CPQ snapshot to FINISHED moves ----
                sol = procurement.values.get("sale_line_id")
                if sol and not getattr(sol, "_name", False):
                    sol = self.env["sale.order.line"].browse(sol)

                if sol and getattr(sol.product_template_id, "cpq_ok", False):
                    # write on finished moves (these are the ones your MO compute depends on)
                    finished_moves = production.move_finished_ids.sudo()
                    finished_moves.write({
                        "sale_line_id": sol.id,
                        "cpq_configuration_json": sol.cpq_configuration_json or False,
                        "cpq_configuration_summary": sol.cpq_configuration_summary or False,
                        # keep these only if you added those fields on stock.move
                        # "cpq_config_hash": sol.cpq_config_hash or False,
                        # "cpq_qr_code_image": sol.cpq_qr_code_image or False,
                    })

                # ---- (Optional) annotate RAW moves with your CPQ BOM metadata ----
                # If you need to mark component moves with cpq_bom_id / cpq_bom_line_id etc.,
                # do it here AFTER confirm, by matching components to your exploded BOM.
                #
                # Example (pseudo):
                # for idx, (component, qty, uom, cpq_bom_line) in enumerate(bom.explode(product, procurement.product_qty)):
                #     moves = production.move_raw_ids.filtered(lambda m: m.product_id == component)
                #     moves.write({
                #         "cpq_bom_id": bom.id,
                #         "cpq_bom_line_id": cpq_bom_line.id,
                #         "cpq_description": f"{product.display_name} - {idx+1}",
                #     })

                # Post messages same as Odoo core (unchanged)
                origin_production = (
                    production.move_dest_ids[:1].raw_material_production_id
                )
                orderpoint = production.orderpoint_id
                if orderpoint and orderpoint.create_uid.id == SUPERUSER_ID and orderpoint.trigger == "manual":
                    production.message_post(
                        body=_("This production order has been created from Replenishment Report."),
                        message_type="comment",
                        subtype_xmlid="mail.mt_note",
                    )
                elif orderpoint:
                    production.message_post_with_view(
                        "mail.message_origin_link",
                        values={"self": production, "origin": orderpoint},
                        subtype_id=self.env.ref("mail.mt_note").id,
                    )
                elif origin_production:
                    production.message_post_with_view(
                        "mail.message_origin_link",
                        values={"self": production, "origin": origin_production},
                        subtype_id=self.env.ref("mail.mt_note").id,
                    )

            else:
                remaining.append((procurement, rule))

        # Let base logic handle everything else
        return super()._run_manufacture(remaining)
    
    
