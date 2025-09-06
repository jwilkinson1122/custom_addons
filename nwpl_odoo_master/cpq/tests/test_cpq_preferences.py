from odoo.tests.common import TransactionCase, tagged

@tagged('post_install', 'at_install')
class TestCpqPreferenceResolver(TransactionCase):

    def setUp(self):
        super().setUp()

        self.partner = self.env['res.partner'].create({
            'name': 'Scoped Partner',
        })

        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_cpq_user',
            'email': 'test@example.com',
            'partner_id': self.partner.id,
        })

        # Common attribute and linked product.attribute
        self.odoo_attr = self.env['product.attribute'].create({'name': 'Linked Odoo Attr'})

        self.cpq_attr = self.env['cpq.attribute'].create({
            'name': 'Scoped Attribute',
            'linked_product_attribute_id': self.odoo_attr.id
        })

        self.cpq_val = self.env['cpq.attribute.value'].create({
            'name': 'Scoped Value',
            'attribute_id': self.cpq_attr.id,
            'price_extra': 15.0,
        })

        # Product Template
        self.template = self.env['product.template'].create({
            'name': 'Scoped Product',
            'type': 'consu',
            'list_price': 120.0,
        })

    def _add_rule(self, scope, note):
        vals = {
            'scope': scope,
            'attribute_id': self.cpq_attr.id,
            'value_id': self.cpq_val.id,
            'note': note,
            'active': True,
        }
        if scope == 'partner':
            vals['partner_id'] = self.partner.id
        elif scope == 'user':
            vals['contact_id'] = self.user.id
        elif scope == 'product':
            vals['product_tmpl_id'] = self.template.id
        self.env['cpq.rules.product'].create(vals)


    def test_resolve_preferences_creates_virtual_ptav(self):
        self._add_rule('global', 'Auto-note')
        resolver = self.env['cpq.preferences.resolver']
        result = resolver.resolve_preferences(partner=self.partner, product_tmpl=self.template)

        detailed = result['detailed']
        self.assertEqual(len(detailed), 1, "Expected one preference result")

        pref = detailed[0]
        self.assertEqual(pref['attribute_id'], self.cpq_attr.id)
        self.assertEqual(pref['attribute_name'], self.cpq_attr.name)
        self.assertEqual(pref['value_id'], self.cpq_val.id)
        self.assertEqual(pref['ptav_name'], self.cpq_val.name)
        self.assertEqual(pref['note'], 'Auto-note')

        self.assertTrue(str(pref['ptav_id']).startswith('NewId'))


    def _assert_preference_found(self, prefs, expected_note):
        self.assertEqual(len(prefs['detailed']), 1)
        pref = prefs['detailed'][0]

        self.assertEqual(pref['attribute_id'], self.cpq_attr.id)
        self.assertEqual(pref['attribute_name'], self.cpq_attr.name)
        self.assertEqual(pref['value_id'], self.cpq_val.id)
        self.assertEqual(pref['ptav_name'], self.cpq_val.name)
        self.assertEqual(pref['note'], expected_note)

        self.assertTrue(str(pref['ptav_id']).startswith("NewId"))


    def test_global_scope_preference(self):
        self._add_rule('global', 'From Global Scope')
        prefs = self.env['cpq.preferences.resolver'].resolve_preferences(
            partner=self.partner, user=self.user, product_tmpl=self.template
        )
        self._assert_preference_found(prefs, 'From Global Scope')

    def test_partner_scope_preference(self):
        self._add_rule('partner', 'From Partner Scope')
        prefs = self.env['cpq.preferences.resolver'].resolve_preferences(
            partner=self.partner, user=self.user, product_tmpl=self.template
        )
        self._assert_preference_found(prefs, 'From Partner Scope')

    def test_user_scope_preference(self):
        self._add_rule('user', 'From User Scope')
        prefs = self.env['cpq.preferences.resolver'].resolve_preferences(
            partner=self.partner, user=self.user, product_tmpl=self.template
        )
        self._assert_preference_found(prefs, 'From User Scope')

    def test_product_scope_preference(self):
        self._add_rule('product', 'From Product Scope')
        prefs = self.env['cpq.preferences.resolver'].resolve_preferences(
            partner=self.partner, user=self.user, product_tmpl=self.template
        )
        self._assert_preference_found(prefs, 'From Product Scope')