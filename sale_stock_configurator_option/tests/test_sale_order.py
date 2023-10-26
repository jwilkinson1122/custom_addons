from odoo.tests import SavepointCase


class SaleOrderCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("sale_configurator_option.sale_order_1")

    def test_validation(self):
        self.sale.action_confirm()
        self.assertEqual(len(self.sale.picking_ids.move_lines), 1)

    def test_picking_validation(self):
        self.sale.action_confirm()
        picking = self.sale.picking_ids
        for move in picking.move_lines:
            move.quantity_done = move.product_qty
        picking.button_validate()
        for line in self.sale.order_line:
            self.assertEqual(line.qty_delivered, line.product_uom_qty)
