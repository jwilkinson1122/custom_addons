from odoo.exceptions import ValidationError

from .common import TestProductDeviceConfiguratorCommon


class TestDeviceConfigure(TestProductDeviceConfiguratorCommon):
    def test_01_device_configure_die_with_counter_die_and_mold(self):
        # GIVEN
        cfg = self.DeviceConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                # die_id omitted, expecting to use default from settings.
                'design_id': self.device_design_f.id,
                'material_id': self.device_material_brass_7.id,
                'material_counter_id': self.device_material_plastic_05.id,
                'difficulty_id': self.device_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 10,
                'quantity_spare_dies': 3,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
                'origin': '1111',
                'ref': '2222',
                # quantity_mold not set, expecting to use default from
                # settings -> 1.
            }
        )
        # WHEN
        res = cfg.action_configure()
        # THEN
        self.assertEqual(cfg.category_counter_die_id, self.product_categ_furniture)
        self.assertEqual(cfg.category_mold_id, self.product_categ_service)
        self.assertEqual(len(res), 3)
        # Die
        self.assertEqual(res['die']['quantity'], 13)
        self.assertEqual(res['die']['price_unit'], 13.5)
        product_die = res['die']['product']
        self.assertEqual(product_die.company_id, self.company_main)
        self.assertEqual(product_die.device_type, 'die')
        self.assertFalse(product_die.is_insert_die)
        self.assertEqual(product_die.weight, 294.0)
        self.assertEqual(product_die.type, 'consu')
        self.assertEqual(product_die.default_code, '1111F1B7 / 2222')
        self.assertEqual(product_die.name, 'Brass Die, HFS, F1, 7 mm+ Spare 3 pcs')
        self.assertEqual(
            product_die.description_sale, '15x10 cm ; A ; 0.09 eur/cm ; 0.5 val'
        )
        self.assertEqual(product_die.categ_id, self.product_categ_consu)
        # Counter Die
        self.assertEqual(res['counter_die']['quantity'], 20)
        self.assertEqual(res['counter_die']['price_unit'], 12)
        product_counter_die = res['counter_die']['product']
        self.assertEqual(product_counter_die.company_id, self.company_main)
        self.assertEqual(product_counter_die.device_type, 'counter_die')
        self.assertFalse(product_counter_die.is_insert_die)
        self.assertEqual(product_counter_die.weight, 126.0)
        self.assertEqual(product_counter_die.type, 'consu')
        self.assertEqual(product_counter_die.default_code, '1111F1P1P0.5 / 2222')
        self.assertEqual(
            product_counter_die.name, 'Plastic Counter-Die, F1, 0.5 mm+ Spare 10 pcs'
        )
        self.assertFalse(product_counter_die.description_sale)
        self.assertEqual(product_counter_die.categ_id, self.product_categ_furniture)
        # Mold
        self.assertEqual(res['mold']['quantity'], 1)
        self.assertEqual(res['mold']['price_unit'], 0.0)
        product_mold = res['mold']['product']
        self.assertEqual(product_mold.company_id, self.company_main)
        self.assertEqual(product_mold.device_type, 'mold')
        self.assertFalse(product_mold.is_insert_die)
        self.assertEqual(product_die.weight, 294)
        self.assertEqual(product_mold.type, 'service')
        self.assertEqual(product_mold.default_code, '1111F1P1 / 2222')
        self.assertEqual(product_mold.name, 'Molding service F1')
        self.assertFalse(product_mold.description_sale)
        self.assertEqual(product_mold.categ_id, self.product_categ_service)
        self.assertFalse(cfg.is_insert_die)
        # WHEN
        on_res = cfg._onchange_die_id()
        # THEN
        self.assertEqual(
            on_res, {'domain': {'product_insert_die_ref_id': [(1, '=', 1)]}}
        )
        for product in product_die | product_counter_die | product_mold:
            # Expect new message to be added with configurator parameters.
            msg = product.message_ids[0]
            self.assertIn(
                'size_length', msg.body, f'Product: {product.name}. Message: {msg.body}'
            )
            tmpl = product.product_tmpl_id
            msg = tmpl.message_ids[0]
            self.assertIn(
                'size_length',
                msg.body,
                f'Product Template: {tmpl.name}. Message: {msg.body}',
            )

    def test_02_device_configure_insert_die_without_counter_die_and_mold(self):
        # GIVEN
        product_ref = self.ProductProduct.create(
            {
                'name': 'Die Ref 1',
                'default_code': '1111F1B7 / 2222',
                'device_type': 'die',
            }
        )
        cfg = self.DeviceConfigure.create(
            {
                'sequence': 2,
                'partner_id': self.partner_azure.id,
                'die_id': self.device_die_insert.id,
                'product_insert_die_ref_id': product_ref.id,
                'design_id': self.device_design_f.id,
                'material_id': self.device_material_brass_7.id,
                'material_counter_id': self.device_material_plastic_05.id,
                'difficulty_id': self.device_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 10,
                'quantity_spare_dies': 3,
                'quantity_counter_dies': 0,
                'quantity_counter_spare_dies': 0,
                'quantity_mold': 0,
                'origin': '1111',
                'ref': '2222',
            }
        )
        # WHEN
        res = cfg.action_configure()
        # THEN
        self.assertEqual(cfg.insert_die_ref, 'F1')
        self.assertEqual(cfg.category_counter_die_id, self.product_categ_furniture)
        self.assertEqual(cfg.category_mold_id, self.product_categ_service)
        self.assertEqual(len(res), 1)
        # Die
        self.assertEqual(res['die']['quantity'], 13)
        self.assertEqual(res['die']['price_unit'], 13.5)
        product_die = res['die']['product']
        self.assertEqual(product_die.device_type, 'die')
        self.assertTrue(product_die.is_insert_die)
        self.assertEqual(product_die.weight, 294.0)
        self.assertEqual(product_die.type, 'consu')
        self.assertEqual(product_die.default_code, '1111F1iF2B7 / 2222')
        self.assertEqual(
            product_die.name, 'Brass Insert Die, HFS, F2, 7 mm+ Spare 3 pcs'
        )
        self.assertEqual(
            product_die.description_sale, '15x10 cm ; A ; 0.09 eur/cm ; 0.5 val'
        )
        self.assertTrue(cfg.is_insert_die)
        # WHEN
        on_res = cfg._onchange_die_id()
        # THEN
        self.assertEqual(
            on_res,
            {
                'domain': {
                    'product_insert_die_ref_id': [
                        ('device_type', '=', 'die'),
                        ('is_insert_die', '=', False),
                    ]
                }
            },
        )

    def test_03_device_configure_categories_missing_or_wrong_device_type(self):
        # GIVEN.
        # No type for die category.
        self.product_categ_consu.device_type = False
        cfg = self.DeviceConfigure.create(
            {
                'sequence': 1,
                'partner_id': self.partner_azure.id,
                'die_id': self.device_die_default.id,
                'design_id': self.device_design_f.id,
                'material_id': self.device_material_brass_7.id,
                'material_counter_id': self.device_material_plastic_05.id,
                'difficulty_id': self.device_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 10,
                'quantity_spare_dies': 3,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
                'quantity_mold': 1,
                'origin': '1111',
                'ref': '2222',
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Die must have Category \(.+\) with Die type!"
        ):
            cfg.action_configure()
        # GIVEN
        self.product_categ_consu.device_type = 'die'
        # Set wrong type for counter die categ.
        self.product_categ_furniture.device_type = 'mold'
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"Counter Die must have Category \(.+\) with Counter Die type!",
        ):
            cfg.action_configure()
        # GIVEN
        self.product_categ_furniture.device_type = 'counter_die'
        self.product_categ_service.device_type = False
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Mold must have Category \(.+\) with Mold type!"
        ):
            cfg.action_configure()
