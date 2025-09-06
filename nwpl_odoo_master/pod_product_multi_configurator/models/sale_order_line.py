import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    length = fields.Float(string='Length')
    
    laterality_mode = fields.Selection([
        ('left_only', 'Left Only'),
        ('right_only', 'Right Only'),
        ('bilateral_shared', 'Bilateral Shared'),
        ('bilateral_split', 'Bilateral Split'),
        ('bilateral_hybrid', 'Bilateral Hybrid'),
    ], string="Laterality Mode", store=True)

    # JSON payload of selections { shared: {...}, left: {...}, right: {...}, hybrid_groups: {...} }
    laterality_payload = fields.Json(string="Laterality Payload", store=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        BILATERAL = {'bilateral_shared', 'bilateral_split', 'bilateral_hybrid'}
        Uom = self.env['uom.uom']
        for vals in vals_list:
            mode = vals.get('laterality_mode') or self.env.context.get('laterality_mode')
            if mode in BILATERAL:
                base_uom = Uom.browse(vals.get('product_uom') or 0) \
                        or self.env['product.product'].browse(vals.get('product_id') or 0).uom_id
                pair = Uom.search([
                    ('category_id', '=', base_uom.category_id.id),
                    ('uom_type', '=', 'bigger'),
                    ('factor_inv', '=', 2),
                ], limit=1)
                if pair:
                    qty_units = float(vals.get('product_uom_qty') or 1.0)
                    qty_pairs = max(1.0, qty_units/2.0) if qty_units >= 2.0 else 1.0
                    vals['product_uom'] = pair.id
                    vals['product_uom_qty'] = qty_pairs
        return super().create(vals_list)
    
    def _laterality_price_adjustments(self):
        """Return an extra price delta based on laterality payload."""
        self.ensure_one()
        payload = self.laterality_payload or {}
        mode = self.laterality_mode
        # Examples:
        # - add per-side surcharge if split/hybrid
        # - add extras from payload maps
        delta = 0.0
        if mode in ('bilateral_split', 'bilateral_hybrid'):
            # e.g., +$X handling fee
            delta += 0.0
        # Walk payload to sum extras if you price attributes separately
        # delta += ...
        return delta

    @api.onchange('laterality_mode', 'laterality_payload')
    def _onchange_laterality_reprice(self):
        for line in self:
            delta = line._laterality_price_adjustments()
            # Let pricelist compute base; add delta after compute
            # If you already override price computation elsewhere, integrate there.
            if delta:
                line.price_unit = (line.price_unit or 0.0) + delta
    
    
    @api.model
    def _pair_uom_for(self, uom):
        """Find Pair(s) in same category (uom_type=bigger, factor_inv=2)."""
        if not uom:
            return False
        return self.env['uom.uom'].search([
            ('category_id', '=', uom.category_id.id),
            ('uom_type', '=', 'bigger'),
            ('factor_inv', '=', 2),
        ], limit=1)
        
    def write(self, vals):
        res = super().write(vals)
        for line in self.filtered(lambda l: l.laterality_mode == 'bilateral_split'):
            payload = line.laterality_payload or {}
            def side_text(side):
                sel = payload.get(side) or {}
                if not sel:
                    return ""
                pavs = self.env['product.attribute.value'].browse([int(v) for v in sel.values()])
                by_attr = {}
                for pav in pavs:
                    by_attr.setdefault(pav.attribute_id.name, []).append(pav.name)
                parts = [f"{k}: {', '.join(vs)}" for k, vs in by_attr.items()]
                return f"\n{side.capitalize()}: " + " ; ".join(parts)
            line.with_context(laterality_name_done=True).write({
                'name': f"{line.product_id.display_name}{side_text('left')}{side_text('right')}"
            })

        return res

    # def write(self, vals):
    #     res = super().write(vals)
    #     if self.env.context.get('laterality_normalized'):
    #         return res

    #     bilat = {'bilateral_shared', 'bilateral_split', 'bilateral_hybrid'}
    #     to_fix = self.filtered(lambda l: l.laterality_mode in bilat)

    #     for line in to_fix:
    #         if not line.product_uom or line.product_uom.uom_type != 'reference':
    #             continue
    #         pair = line._pair_uom_for(line.product_uom)
    #         if not pair:
    #             continue
    #         if line.product_uom_qty and (line.product_uom_qty % 2.0 == 0.0):
    #             line.with_context(laterality_normalized=True).write({
    #                 'product_uom': pair.id,
    #                 'product_uom_qty': line.product_uom_qty / 2.0,
    #             })
    #     return res
                      
    # def write(self, vals):
    #     res = super().write(vals)
    #     for line in self:
    #         _logger.info("SOL laterality persisted id=%s mode=%s payload_keys=%s qty=%s uom=%s",
    #                      line.id, line.laterality_mode, list((line.laterality_payload or {}).keys()),
    #                      line.product_uom_qty, line.product_uom.display_name if line.product_uom else None)
    #     return res
