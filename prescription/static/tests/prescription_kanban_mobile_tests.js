odoo.define('prescription.prescriptionKanbanMobileTests', function (require) {
"use strict";

const PrescriptionKanbanView = require('prescription.PrescriptionKanbanView');

const testUtils = require('web.test_utils');
const {createPrescriptionView, mockPrescriptionRPC} = require('prescription.test_utils');

QUnit.module('Views');

QUnit.module('PrescriptionKanbanView Mobile', {
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
                },
                records: [
                    {id: 1, name: "Office 1"},
                    {id: 2, name: "Office 2"},
                ],
            },
        };
        this.regularInfos = {
            user_location: [2, "Office 2"],
        };
    },
}, function () {
    QUnit.test('basic rendering', async function (assert) {
        assert.expect(7);

        const kanban = await createPrescriptionView({
            View: PrescriptionKanbanView,
            model: 'product',
            data: this.data,
            arch: `
                <kanban>
                    <templates>
                        <t t-name="kanban-box">
                            <div><field name="name"/></div>
                        </t>
                    </templates>
                </kanban>
            `,
            mockRPC: mockPrescriptionRPC({
                infos: this.regularInfos,
                userLocation: this.data['prescription.location'].records[0].id,
            }),
        });

        assert.containsOnce(kanban, '.o_kanban_view .o_kanban_record:not(.o_kanban_ghost)',
            "should have 1 records in the renderer");

        // check view layout
        assert.containsOnce(kanban, '.o_content > .o_prescription_content',
            "should have a 'kanban prescription wrapper' column");
        assert.containsOnce(kanban, '.o_prescription_content > .o_kanban_view',
            "should have a 'classical kanban view' column");
        assert.hasClass(kanban.$('.o_kanban_view'), 'o_prescription_kanban_view',
            "should have classname 'o_prescription_kanban_view'");
        assert.containsOnce($('.o_prescription_content'), '> details',
            "should have a 'prescription kanban' details/summary discolure panel");
        assert.hasClass($('.o_prescription_content > details'), 'fixed-bottom',
            "should have classname 'fixed-bottom'");
        assert.isNotVisible($('.o_prescription_content > details .o_prescription_banner'),
            "shouldn't have a visible 'prescription kanban' banner");

        kanban.destroy();
    });

    QUnit.module('PrescriptionWidget', function () {
        QUnit.test('toggle', async function (assert) {
            assert.expect(6);

            const kanban = await createPrescriptionView({
                View: PrescriptionKanbanView,
                model: 'product',
                data: this.data,
                arch: `
                    <kanban>
                        <templates>
                            <t t-name="kanban-box">
                                <div><field name="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC: mockPrescriptionRPC({
                    infos: Object.assign({}, this.regularInfos, {
                        total: "3.00",
                    }),
                    userLocation: this.data['prescription.location'].records[0].id,
                }),
            });

            const $details = $('.o_prescription_content > details');
            assert.isNotVisible($details.find('.o_prescription_banner'),
                "shouldn't have a visible 'prescription kanban' banner");
            assert.isVisible($details.find('> summary'),
                "should hava a visible cart toggle button");
            assert.containsOnce($details, '> summary:contains(Your cart)',
                "should have 'Your cart' in the button text");
            assert.containsOnce($details, '> summary:contains(3.00)',
                "should have '3.00' in the button text");

            await testUtils.dom.click($details.find('> summary'));
            assert.isVisible($details.find('.o_prescription_banner'),
                "should have a visible 'prescription kanban' banner");

            await testUtils.dom.click($details.find('> summary'));
            assert.isNotVisible($details.find('.o_prescription_banner'),
                "shouldn't have a visible 'prescription kanban' banner");

            kanban.destroy();
        });

        QUnit.test('keep open when adding quantities', async function (assert) {
            assert.expect(6);

            const kanban = await createPrescriptionView({
                View: PrescriptionKanbanView,
                model: 'product',
                data: this.data,
                arch: `
                    <kanban>
                        <templates>
                            <t t-name="kanban-box">
                                <div><field name="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC: mockPrescriptionRPC({
                    infos: Object.assign({}, this.regularInfos, {
                        lines: [
                            {
                                id: 6,
                                product: [1, "Tuna sandwich", "3.00"],
                                options: [],
                                quantity: 1.0,
                            },
                        ],
                    }),
                    userLocation: this.data['prescription.location'].records[0].id,
                }),
            });

            const $details = $('.o_prescription_content > details');
            assert.isNotVisible($details.find('.o_prescription_banner'),
                "shouldn't have a visible 'prescription kanban' banner");
            assert.isVisible($details.find('> summary'),
                "should hava a visible cart toggle button");

            await testUtils.dom.click($details.find('> summary'));
            assert.isVisible($details.find('.o_prescription_banner'),
                "should have a visible 'prescription kanban' banner");

            const $widgetSecondColumn = kanban.$('.o_prescription_widget .o_prescription_widget_info:eq(1)');

            assert.containsOnce($widgetSecondColumn, '.o_prescription_widget_lines > li',
                "should have 1 order line");

            let $firstLine = $widgetSecondColumn.find('.o_prescription_widget_lines > li:first');

            await testUtils.dom.click($firstLine.find('button.o_add_product'));
            assert.isVisible($('.o_prescription_content > details .o_prescription_banner'),
                "add quantity should keep 'prescription kanban' banner open");

            $firstLine = kanban.$('.o_prescription_widget .o_prescription_widget_info:eq(1) .o_prescription_widget_lines > li:first');

            await testUtils.dom.click($firstLine.find('button.o_remove_product'));
            assert.isVisible($('.o_prescription_content > details .o_prescription_banner'),
                "remove quantity should keep 'prescription kanban' banner open");

            kanban.destroy();
        });
    });
});

});
