# -*- coding: utf-8 -*-


from collections import defaultdict

from odoo import api, fields, models, _
from odoo.tools.sql import column_exists, create_column


class StockRoute(models.Model):
    _inherit = "stock.route"
    prescriptions_selectable = fields.Boolean("Selectable on Prescriptions Order Line")


class StockMove(models.Model):
    _inherit = "stock.move"
    prescriptions_line_id = fields.Many2one('prescriptions.order.line', 'Prescription Line', index='btree_not_null')

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('prescriptions_line_id')
        return distinct_fields

    def _get_related_invoices(self):
        """ Overridden from stock_account to return the customer invoices
        related to this stock move.
        """
        rslt = super(StockMove, self)._get_related_invoices()
        invoices = self.mapped('picking_id.prescriptions_id.invoice_ids').filtered(lambda x: x.state == 'posted')
        rslt += invoices
        #rslt += invoices.mapped('reverse_entry_ids')
        return rslt

    def _get_source_document(self):
        res = super()._get_source_document()
        return self.prescriptions_line_id.order_id or res

    def _get_prescriptions_order_lines(self):
        """ Return all possible prescriptions order lines for one or multiple stock moves. """
        def _get_origin_moves(move):
            origin_moves = move.move_orig_ids
            if origin_moves:
                origin_moves += _get_origin_moves(origin_moves)
            return origin_moves

        def _get_destination_moves(move):
            destination_moves = move.move_dest_ids
            if destination_moves:
                destination_moves += _get_destination_moves(destination_moves)
            return destination_moves

        return (self + _get_origin_moves(self) + _get_destination_moves(self)).prescriptions_line_id

    def _assign_picking_post_process(self, new=False):
        super(StockMove, self)._assign_picking_post_process(new=new)
        if new:
            picking_id = self.mapped('picking_id')
            prescriptions_order_ids = self.mapped('prescriptions_line_id.order_id')
            for prescriptions_order_id in prescriptions_order_ids:
                picking_id.message_post_with_source(
                    'mail.message_origin_link',
                    render_values={'self': picking_id, 'origin': prescriptions_order_id},
                    subtype_xmlid='mail.mt_note',
                )

    def _get_all_related_sm(self, product):
        return super()._get_all_related_sm(product) | self.filtered(lambda m: m.prescriptions_line_id.product_id == product)

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    prescriptions_id = fields.Many2one('prescriptions.order', 'Prescription Order')


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['prescriptions_line_id', 'partner_id', 'sequence']
        return fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    prescriptions_id = fields.Many2one(related="group_id.prescriptions_id", string="Prescriptions Order", store=True, index='btree_not_null')

    def _auto_init(self):
        """
        Create related field here, too slow
        when computing it afterwards through _compute_related.

        Since group_id.prescriptions_id is created in this module,
        no need for an UPDATE statement.
        """
        if not column_exists(self.env.cr, 'stock_picking', 'prescriptions_id'):
            create_column(self.env.cr, 'stock_picking', 'prescriptions_id', 'int4')
        return super()._auto_init()

    def _action_done(self):
        res = super()._action_done()
        prescriptions_order_lines_vals = []
        for move in self.move_ids:
            prescriptions_order = move.picking_id.prescriptions_id
            # Creates new RX line only when pickings linked to a prescriptions order and
            # for moves with qty. done and not already linked to a RX line.
            if not prescriptions_order or move.location_dest_id.usage != 'customer' or move.prescriptions_line_id or not move.picked:
                continue
            product = move.product_id
            rx_line_vals = {
                'move_ids': [(4, move.id, 0)],
                'name': product.display_name,
                'order_id': prescriptions_order.id,
                'product_id': product.id,
                'product_uom_qty': 0,
                'qty_delivered': move.quantity,
                'product_uom': move.product_uom.id,
            }
            if product.invoice_policy == 'delivery':
                # Check if there is already a RX line for this product to get
                # back its unit price (in case it was manually updated).
                rx_line = prescriptions_order.order_line.filtered(lambda rxl: rxl.product_id == product)
                if rx_line:
                    rx_line_vals['price_unit'] = rx_line[0].price_unit
            elif product.invoice_policy == 'order':
                # No unit price if the product is invoiced on the ordered qty.
                rx_line_vals['price_unit'] = 0
            prescriptions_order_lines_vals.append(rx_line_vals)

        if prescriptions_order_lines_vals:
            self.env['prescriptions.order.line'].with_context(skip_procurement=True).create(prescriptions_order_lines_vals)
        return res

    def _log_less_quantities_than_expected(self, moves):
        """ Log an activity on prescriptions order that are linked to moves. The
        note summarize the real processed quantity and promote a
        manual action.

        :param dict moves: a dict with a move as key and tuple with
        new and old quantity as value. eg: {move_1 : (4, 5)}
        """

        def _keys_in_groupby(prescriptions_line):
            """ group by order_id and the prescriptions_person on the order """
            return (prescriptions_line.order_id, prescriptions_line.order_id.user_id)

        def _render_note_exception_quantity(moves_information):
            """ Generate a note with the picking on which the action
            occurred and a summary on impacted quantity that are
            related to the prescriptions order where the note will be logged.

            :param moves_information dict:
            {'move_id': ['prescriptions_order_line_id', (new_qty, old_qty)], ..}

            :return: an html string with all the information encoded.
            :rtype: str
            """
            origin_moves = self.env['stock.move'].browse([move.id for move_orig in moves_information.values() for move in move_orig[0]])
            origin_picking = origin_moves.mapped('picking_id')
            values = {
                'origin_moves': origin_moves,
                'origin_picking': origin_picking,
                'moves_information': moves_information.values(),
            }
            return self.env['ir.qweb']._render('pod_prescriptions_stock.exception_on_picking', values)

        documents = self.sudo()._log_activity_get_documents(moves, 'prescriptions_line_id', 'DOWN', _keys_in_groupby)
        self._log_activity(_render_note_exception_quantity, documents)

        return super(StockPicking, self)._log_less_quantities_than_expected(moves)

class StockLot(models.Model):
    _inherit = 'stock.lot'

    prescriptions_order_ids = fields.Many2many('prescriptions.order', string="Prescriptions Orders", compute='_compute_prescriptions_order_ids')
    prescriptions_order_count = fields.Integer('Prescription order count', compute='_compute_prescriptions_order_ids')

    @api.depends('name')
    def _compute_prescriptions_order_ids(self):
        prescriptions_orders = defaultdict(lambda: self.env['prescriptions.order'])
        for move_line in self.env['stock.move.line'].search([('lot_id', 'in', self.ids), ('state', '=', 'done')]):
            move = move_line.move_id
            if move.picking_id.location_dest_id.usage == 'customer' and move.prescriptions_line_id.order_id:
                prescriptions_orders[move_line.lot_id.id] |= move.prescriptions_line_id.order_id
        for lot in self:
            lot.prescriptions_order_ids = prescriptions_orders[lot.id]
            lot.prescriptions_order_count = len(lot.prescriptions_order_ids)

    def action_view_rx(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("pod_prescriptions.action_orders")
        action['domain'] = [('id', 'in', self.mapped('prescriptions_order_ids.id'))]
        action['context'] = dict(self._context, create=False)
        return action
