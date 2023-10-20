/** @odoo-module **/

import {
    afterEach,
    afterNextRender,
    beforeEach,
    start,
} from '@mail/utils/test_utils';

import FormView from 'web.FormView';
import KanbanView from 'web.KanbanView';
import ListView from 'web.ListView';
import { Many2OneAvatarPractitioner } from '@pod_manager/js/m2x_avatar_practitioner';
import { dom, mock } from 'web.test_utils';

QUnit.module('pod_manager', {}, function () {
    QUnit.module('M2XAvatarPractitioner', {
        beforeEach() {
            beforeEach(this);

            // reset the cache before each test
            Many2OneAvatarPractitioner.prototype.partnerIds = {};

            Object.assign(this.data, {
                'foo': {
                    fields: {
                        practitioner_id: { string: "Practitioner", type: 'many2one', relation: 'pod.practitioner.public' },
                        practitioner_ids: { string: "Practitioners", type: "many2many", relation: 'pod.practitioner.public' },
                    },
                    records: [
                        { id: 1, practitioner_id: 11, practitioner_ids: [11, 23] },
                        { id: 2, practitioner_id: 7 },
                        { id: 3, practitioner_id: 11 },
                        { id: 4, practitioner_id: 23 },
                    ],
                },
            });
            this.data['pod.practitioner.public'].records.push(
                { id: 11, name: "Mario", user_id: 11, user_partner_id: 11 },
                { id: 7, name: "Luigi", user_id: 12, user_partner_id: 12 },
                { id: 23, name: "Yoshi", user_id: 13, user_partner_id: 13 }
            );
            this.data['res.users'].records.push(
                { id: 11, partner_id: 11 },
                { id: 12, partner_id: 12 },
                { id: 13, partner_id: 13 }
            );
            this.data['res.partner'].records.push(
                { id: 11, display_name: "Mario" },
                { id: 12, display_name: "Luigi" },
                { id: 13, display_name: "Yoshi" }
            );
        },
        afterEach() {
            afterEach(this);
        },
    });

    QUnit.test('many2one_avatar_practitioner widget in list view', async function (assert) {
        assert.expect(11);

        const { widget: list } = await start({
            hasChatWindow: true,
            hasView: true,
            View: ListView,
            model: 'foo',
            data: this.data,
            arch: '<tree><field name="practitioner_id" widget="many2one_avatar_practitioner"/></tree>',
            mockRPC(route, args) {
                if (args.method === 'read') {
                    assert.step(`read ${args.model} ${args.args[0]}`);
                }
                return this._super(...arguments);
            },
        });

        assert.strictEqual(list.$('.o_data_cell span').text(), 'MarioLuigiMarioYoshi');

        // click on first practitioner
        await afterNextRender(() =>
            dom.click(list.$('.o_data_cell:nth(0) .o_m2o_avatar > img'))
        );
        assert.verifySteps(
            ['read pod.practitioner.public 11'],
            "first practitioner should have been read to find its partner"
        );
        assert.containsOnce(
            document.body,
            '.o_ChatWindowHeader_name',
            'should have opened chat window'
        );
        assert.strictEqual(
            document.querySelector('.o_ChatWindowHeader_name').textContent,
            "Mario",
            'chat window should be with clicked practitioner'
        );

        // click on second practitioner
        await afterNextRender(() =>
            dom.click(list.$('.o_data_cell:nth(1) .o_m2o_avatar > img')
        ));
        assert.verifySteps(
            ['read pod.practitioner.public 7'],
            "second practitioner should have been read to find its partner"
        );
        assert.containsN(
            document.body,
            '.o_ChatWindowHeader_name',
            2,
            'should have opened second chat window'
        );
        assert.strictEqual(
            document.querySelectorAll('.o_ChatWindowHeader_name')[1].textContent,
            "Luigi",
            'chat window should be with clicked practitioner'
        );

        // click on third practitioner (same as first)
        await afterNextRender(() =>
            dom.click(list.$('.o_data_cell:nth(2) .o_m2o_avatar > img'))
        );
        assert.verifySteps(
            [],
            "practitioner should not have been read again because we already know its partner"
        );
        assert.containsN(
            document.body,
            '.o_ChatWindowHeader_name',
            2,
            "should still have only 2 chat windows because third is the same partner as first"
        );

        list.destroy();
    });

    QUnit.test('many2one_avatar_practitioner widget in kanban view', async function (assert) {
        assert.expect(6);

        const { widget: kanban } = await start({
            hasView: true,
            View: KanbanView,
            model: 'foo',
            data: this.data,
            arch: `
                <kanban>
                    <templates>
                        <t t-name="kanban-box">
                            <div>
                                <field name="practitioner_id" widget="many2one_avatar_practitioner"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
        });

        assert.strictEqual(kanban.$('.o_kanban_record').text().trim(), '');
        assert.containsN(kanban, '.o_m2o_avatar', 4);
        assert.strictEqual(kanban.$('.o_m2o_avatar:nth(0) > img').data('src'), '/web/image/pod.practitioner.public/11/avatar_128');
        assert.strictEqual(kanban.$('.o_m2o_avatar:nth(1) > img').data('src'), '/web/image/pod.practitioner.public/7/avatar_128');
        assert.strictEqual(kanban.$('.o_m2o_avatar:nth(2) > img').data('src'), '/web/image/pod.practitioner.public/11/avatar_128');
        assert.strictEqual(kanban.$('.o_m2o_avatar:nth(3) > img').data('src'), '/web/image/pod.practitioner.public/23/avatar_128');

        kanban.destroy();
    });

    QUnit.test('many2one_avatar_practitioner: click on an practitioner not associated with a user', async function (assert) {
        assert.expect(6);

        this.data['pod.practitioner.public'].records[0].user_id = false;
        this.data['pod.practitioner.public'].records[0].user_partner_id = false;
        const { widget: form } = await start({
            hasView: true,
            View: FormView,
            model: 'foo',
            data: this.data,
            arch: '<form><field name="practitioner_id" widget="many2one_avatar_practitioner"/></form>',
            mockRPC(route, args) {
                if (args.method === 'read') {
                    assert.step(`read ${args.model} ${args.args[0]}`);
                }
                return this._super(...arguments);
            },
            res_id: 1,
            services: {
                notification: {
                    notify(notification) {
                        assert.ok(
                            true,
                            "should display a toast notification after failing to open chat"
                        );
                        assert.strictEqual(
                            notification.message,
                            "You can only chat with practitioners that have a dedicated user.",
                            "should display the correct information in the notification"
                        );
                    },
                },
            },
        });

        mock.intercept(form, 'call_service', (ev) => {
            if (ev.data.service === 'notification') {
                assert.step(`display notification "${ev.data.args[0].message}"`);
            }
        }, true);

        assert.strictEqual(form.$('.o_field_widget[name=practitioner_id]').text().trim(), 'Mario');

        await dom.click(form.$('.o_m2o_avatar > img'));

        assert.verifySteps([
            'read foo 1',
            'read pod.practitioner.public 11',
        ]);

        form.destroy();
    });

    QUnit.test('many2many_avatar_practitioner widget in form view', async function (assert) {
        assert.expect(8);

        const { widget: form } = await start({
            hasChatWindow: true,
            hasView: true,
            View: FormView,
            model: 'foo',
            data: this.data,
            arch: '<form><field name="practitioner_ids" widget="many2many_avatar_practitioner"/></form>',
            mockRPC(route, args) {
                if (args.method === 'read') {
                    assert.step(`read ${args.model} ${args.args[0]}`);
                }
                return this._super(...arguments);
            },
            res_id: 1,
        });

        assert.containsN(form, '.o_field_many2manytags.avatar.o_field_widget .badge', 2,
            "should have 2 records");
        assert.strictEqual(form.$('.o_field_many2manytags.avatar.o_field_widget .badge:first img').data('src'),
            '/web/image/pod.practitioner.public/11/avatar_128',
            "should have correct avatar image");

        await dom.click(form.$('.o_field_many2manytags.avatar .badge:first .o_m2m_avatar'));
        await dom.click(form.$('.o_field_many2manytags.avatar .badge:nth(1) .o_m2m_avatar'));

        assert.verifySteps([
            "read foo 1",
            'read pod.practitioner.public 11,23',
            "read pod.practitioner.public 11",
            "read pod.practitioner.public 23",
        ]);

        assert.containsN(
            document.body,
            '.o_ChatWindowHeader_name',
            2,
            "should have 2 chat windows"
        );

        form.destroy();
    });

    QUnit.test('many2many_avatar_practitioner widget in list view', async function (assert) {
        assert.expect(10);

        const { widget: list } = await start({
            hasChatWindow: true,
            hasView: true,
            View: ListView,
            model: 'foo',
            data: this.data,
            arch: '<tree><field name="practitioner_ids" widget="many2many_avatar_practitioner"/></tree>',
            mockRPC(route, args) {
                if (args.method === 'read') {
                    assert.step(`read ${args.model} ${args.args[0]}`);
                }
                return this._super(...arguments);
            },
        });

        assert.containsN(list, '.o_data_cell:first .o_field_many2manytags > span', 2,
            "should have two avatar");

        // click on first practitioner badge
        await afterNextRender(() =>
            dom.click(list.$('.o_data_cell:nth(0) .o_m2m_avatar:first'))
        );
        assert.verifySteps(
            ['read pod.practitioner.public 11,23', "read pod.practitioner.public 11"],
            "first practitioner should have been read to find its partner"
        );
        assert.containsOnce(
            document.body,
            '.o_ChatWindowHeader_name',
            'should have opened chat window'
        );
        assert.strictEqual(
            document.querySelector('.o_ChatWindowHeader_name').textContent,
            "Mario",
            'chat window should be with clicked practitioner'
        );

        // click on second practitioner
        await afterNextRender(() =>
            dom.click(list.$('.o_data_cell:nth(0) .o_m2m_avatar:nth(1)')
            ));
        assert.verifySteps(
            ['read pod.practitioner.public 23'],
            "second practitioner should have been read to find its partner"
        );
        assert.containsN(
            document.body,
            '.o_ChatWindowHeader_name',
            2,
            'should have opened second chat window'
        );
        assert.strictEqual(
            document.querySelectorAll('.o_ChatWindowHeader_name')[1].textContent,
            "Yoshi",
            'chat window should be with clicked practitioner'
        );

        list.destroy();
    });

    QUnit.test('many2many_avatar_practitioner widget in kanban view', async function (assert) {
        assert.expect(7);

        const { widget: kanban } = await start({
            hasView: true,
            View: KanbanView,
            model: 'foo',
            data: this.data,
            arch: `
                <kanban>
                    <templates>
                        <t t-name="kanban-box">
                            <div>
                                <div class="oe_kanban_footer">
                                    <div class="o_kanban_record_bottom">
                                        <div class="oe_kanban_bottom_right">
                                            <field name="practitioner_ids" widget="many2many_avatar_practitioner"/>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
            mockRPC(route, args) {
                if (args.method === 'read') {
                    assert.step(`read ${args.model} ${args.args[0]}`);
                }
                return this._super(...arguments);
            },
        });

        assert.containsN(kanban, '.o_kanban_record:first .o_field_many2manytags img.o_m2m_avatar', 2,
            "should have 2 avatar images");
        assert.strictEqual(kanban.$('.o_kanban_record:first .o_field_many2manytags img.o_m2m_avatar:first').data('src'),
            "/web/image/pod.practitioner.public/11/avatar_128",
            "should have correct avatar image");
        assert.strictEqual(kanban.$('.o_kanban_record:first .o_field_many2manytags img.o_m2m_avatar:eq(1)').data('src'),
            "/web/image/pod.practitioner.public/23/avatar_128",
            "should have correct avatar image");

        await dom.click(kanban.$('.o_kanban_record:first .o_m2m_avatar:nth(0)'));
        await dom.click(kanban.$('.o_kanban_record:first .o_m2m_avatar:nth(1)'));

        assert.verifySteps([
            "read pod.practitioner.public 11,23",
            "read pod.practitioner.public 11",
            "read pod.practitioner.public 23"
        ]);

        kanban.destroy();
    });

    QUnit.test('many2many_avatar_practitioner: click on an practitioner not associated with a user', async function (assert) {
        assert.expect(10);

        this.data['pod.practitioner.public'].records[0].user_id = false;
        this.data['pod.practitioner.public'].records[0].user_partner_id = false;
        const { widget: form } = await start({
            hasChatWindow: true,
            hasView: true,
            View: FormView,
            model: 'foo',
            data: this.data,
            arch: '<form><field name="practitioner_ids" widget="many2many_avatar_practitioner"/></form>',
            mockRPC(route, args) {
                if (args.method === 'read') {
                    assert.step(`read ${args.model} ${args.args[0]}`);
                }
                return this._super(...arguments);
            },
            res_id: 1,
            services: {
                notification: {
                    notify(notification) {
                        assert.ok(
                            true,
                            "should display a toast notification after failing to open chat"
                        );
                        assert.strictEqual(
                            notification.message,
                            "You can only chat with practitioners that have a dedicated user.",
                            "should display the correct information in the notification"
                        );
                    },
                },
            },
        });

        mock.intercept(form, 'call_service', (ev) => {
            if (ev.data.service === 'notification') {
                assert.step(`display notification "${ev.data.args[0].message}"`);
            }
        }, true);

        assert.containsN(form, '.o_field_many2manytags.avatar.o_field_widget .badge', 2,
            "should have 2 records");
        assert.strictEqual(form.$('.o_field_many2manytags.avatar.o_field_widget .badge:first img').data('src'),
            '/web/image/pod.practitioner.public/11/avatar_128',
            "should have correct avatar image");

        await dom.click(form.$('.o_field_many2manytags.avatar .badge:first .o_m2m_avatar'));
        await dom.click(form.$('.o_field_many2manytags.avatar .badge:nth(1) .o_m2m_avatar'));

        assert.verifySteps([
            'read foo 1',
            'read pod.practitioner.public 11,23',
            "read pod.practitioner.public 11",
            "read pod.practitioner.public 23"
        ]);

        assert.containsOnce(document.body, '.o_ChatWindowHeader_name',
            "should have 1 chat window");

        form.destroy();
    });
});
