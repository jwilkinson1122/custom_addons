odoo.define('prescription.prescriptionListTests', function (require) {
"use strict";

const PrescriptionListView = require('prescription.PrescriptionListView');

const testUtils = require('web.test_utils');
const {createPrescriptionView, mockPrescriptionRPC} = require('prescription.test_utils');

QUnit.module('Views');

QUnit.module('PrescriptionListView', {
    beforeEach() {
        const PORTAL_GROUP_ID = 1234;

        this.data = {
            'product': {
                fields: {
                    is_available_at: {string: 'Product Availability', type: 'many2one', relation: 'prescription.location'},
                    category_id: {string: 'Product Category', type: 'many2one', relation: 'prescription.product.category'},
                    partner_id: {string: 'Partner', type: 'many2one', relation: 'prescription.partner'},
                },
                records: [
                    {id: 1, name: 'Tuna sandwich', is_available_at: 1},
                ],
            },
            'prescription.order': {
                fields: {},
                update_quantity() {
                    return Promise.resolve();
                },
            },
            'prescription.product.category': {
                fields: {},
                records: [],
            },
            'prescription.partner': {
                fields: {},
                records: [],
            },
            'prescription.location': {
                fields: {
                    name: {string: 'Name', type: 'char'},
                    company_id: {string: 'Company', type: 'many2one', relation: 'res.company'},
                },
                records: [
                    {id: 1, name: "Office 1", company_id: false},
                    {id: 2, name: "Office 2", company_id: false},
                ],
            },
            'res.users': {
                fields: {
                    name: {string: 'Name', type: 'char'},
                    groups_id: {string: 'Groups', type: 'many2many'},
                },
                records: [
                    {id: 1, name: "Mitchell Admin", groups_id: []},
                    {id: 2, name: "Marc Demo", groups_id: []},
                    {id: 3, name: "Jean-Luc Portal", groups_id: [PORTAL_GROUP_ID]},
                ],
            },
            'res.company': {
                fields: {
                    name: {string: 'Name', type: 'char'},
                }, records: [
                    {id: 1, name: "Dunder Trade Company"},
                ]
            }
        };
        this.regularInfos = {
            username: "Marc Demo",
            wallet: 36.5,
            is_manager: false,
            group_portal_id: PORTAL_GROUP_ID,
            currency: {
                symbol: "\u20ac",
                position: "after"
            },
            user_location: [2, "Office 2"],
            alerts: [{id: 42, message: '<b>Warning! Neurotoxin pressure has reached dangerously unlethal levels.</b>'}]
        };
    },
}, function () {
    QUnit.test('basic rendering', async function (assert) {
        assert.expect(9);

        const list = await createPrescriptionView({
            View: PrescriptionListView,
            model: 'product',
            data: this.data,
            arch: `
                <tree>
                    <field name="name"/>
                </tree>
            `,
            mockRPC: mockPrescriptionRPC({
                infos: this.regularInfos,
                userLocation: this.data['prescription.location'].records[0].id,
            }),
        });

        // check view layout
        assert.containsN(list, '.o_content > div', 2,
            "should have 2 columns");
        assert.containsOnce(list, '.o_content > div.o_search_panel',
            "should have a 'prescription filters' column");
        assert.containsOnce(list, '.o_content > .o_prescription_content',
            "should have a 'prescription wrapper' column");
        assert.containsOnce(list, '.o_prescription_content > .o_list_view',
            "should have a 'classical list view' column");
        assert.hasClass(list.$('.o_list_view'), 'o_prescription_list_view',
            "should have classname 'o_prescription_list_view'");
        assert.containsOnce(list, '.o_prescription_content > span > .o_prescription_banner',
            "should have a 'prescription' banner");

        const $alertMessage = list.$('.alert > *');
        assert.equal($alertMessage.length, 1);
        assert.equal($alertMessage.prop('tagName'), 'B');
        assert.equal($alertMessage.text(), "Warning! Neurotoxin pressure has reached dangerously unlethal levels.")

        list.destroy();
    });

    QUnit.module('PrescriptionWidget', function () {

        QUnit.test('search panel domain location', async function (assert) {
            assert.expect(18);
            let expectedLocation = 1;
            let locationId = this.data['prescription.location'].records[0].id;
            const regularInfos = _.extend({}, this.regularInfos);

            const list = await createPrescriptionView({
                View: PrescriptionListView,
                model: 'product',
                data: this.data,
                arch: `
                    <tree>
                        <field name="name"/>
                    </tree>
                `,
                mockRPC: function (route, args) {
                    assert.step(route);

                    if (route.startsWith('/prescription')) {
                        if (route === '/prescription/user_location_set') {
                            locationId = args.location_id;
                            return Promise.resolve(true);
                        }
                        return mockPrescriptionRPC({
                            infos: regularInfos,
                            userLocation: locationId,
                        }).apply(this, arguments);
                    }
                    if (args.method === 'search_panel_select_multi_range') {
                        assert.deepEqual(args.kwargs.search_domain, [["is_available_at", "in", [expectedLocation]]],
                            'The initial domain of the search panel must contain the user location');
                    }
                    if (route === '/web/dataset/search_read') {
                        assert.deepEqual(args.domain, [["is_available_at", "in", [expectedLocation]]],
                            'The domain for fetching actual data should be correct');
                    }
                    return this._super.apply(this, arguments);
                },
            });

            expectedLocation = 2;
            await testUtils.fields.many2one.clickOpenDropdown('locations');
            await testUtils.fields.many2one.clickItem('locations', "Office 2");

            assert.verifySteps([
                // Initial state
                '/prescription/user_location_get',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/search_read',
                '/prescription/infos',
                // Click m2o
                '/web/dataset/call_kw/prescription.location/name_search',
                // Click new location
                '/prescription/user_location_set',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/search_read',
                '/prescription/infos',
            ]);

            list.destroy();
        });

        QUnit.test('search panel domain location false: fetch products in all locations', async function (assert) {
            assert.expect(9);
            const regularInfos = _.extend({}, this.regularInfos);

            const list = await createPrescriptionView({
                View: PrescriptionListView,
                model: 'product',
                data: this.data,
                arch: `
                    <tree>
                        <field name="name"/>
                    </tree>
                `,
                mockRPC: function (route, args) {
                    assert.step(route);

                    if (route.startsWith('/prescription')) {
                        return mockPrescriptionRPC({
                            infos: regularInfos,
                            userLocation: false,
                        }).apply(this, arguments);
                    }
                    if (args.method === 'search_panel_select_multi_range') {
                        assert.deepEqual(args.kwargs.search_domain, [],
                            'The domain should not exist since the location is false.');
                    }
                    if (route === '/web/dataset/search_read') {
                        assert.deepEqual(args.domain, [],
                            'The domain for fetching actual data should be correct');
                    }
                    return this._super.apply(this, arguments);
                }
            });
            assert.verifySteps([
                '/prescription/user_location_get',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/search_read',
                '/prescription/infos',
            ])

            list.destroy();
        });

        QUnit.test('add a product', async function (assert) {
            assert.expect(1);

            const list = await createPrescriptionView({
                View: PrescriptionListView,
                model: 'product',
                data: this.data,
                arch: `
                    <tree>
                        <field name="name"/>
                    </tree>
                `,
                mockRPC: mockPrescriptionRPC({
                    infos: this.regularInfos,
                    userLocation: this.data['prescription.location'].records[0].id,
                }),
                intercepts: {
                    do_action: function (ev) {
                        assert.deepEqual(ev.data.action, {
                            name: "Configure Your Order",
                            res_model: 'prescription.order',
                            type: 'ir.actions.act_window',
                            views: [[false, 'form']],
                            target: 'new',
                            context: {
                                default_product_id: 1,
                            },
                        },
                        "should open the wizard");
                    },
                },
            });

            await testUtils.dom.click(list.$('.o_data_row:first'));

            list.destroy();
        });
    });
});

});
