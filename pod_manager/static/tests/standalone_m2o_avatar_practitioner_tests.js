/** @odoo-module **/

    const { xml } = owl.tags;

    import AbstractRendererOwl from 'web.AbstractRendererOwl';
    import BasicView from "web.BasicView";
    import BasicRenderer from "web.BasicRenderer";
    import RendererWrapper from 'web.RendererWrapper';
    import { createView } from 'web.test_utils';

    import StandaloneM2OAvatarPractitioner from '@pod_manager/js/standalone_m2o_avatar_practitioner';

    function getHtmlRenderer(html) {
        return BasicRenderer.extend({
            start: function () {
                this.$el.html(html);
                return this._super.apply(this, arguments);
            }
        });
    }

    function getOwlView(owlRenderer, viewType) {
        viewType = viewType || "test";
        return BasicView.extend({
            viewType: viewType,
            config: Object.assign({}, BasicView.prototype.config, {
                Renderer: owlRenderer,
            }),
            getRenderer() {
                return new RendererWrapper(null, this.config.Renderer, {});
            }
        });
    }

    function getHtmlView(html, viewType) {
        viewType = viewType || "test";
        return BasicView.extend({
            viewType: viewType,
            config: Object.assign({}, BasicView.prototype.config, {
                Renderer: getHtmlRenderer(html)
            })
        });
    }

    QUnit.module('pod_manager', {}, function () {
        QUnit.module('StandaloneM2OPractitionerTests', {
            beforeEach: function () {
                this.data = {
                    'foo': {
                        fields: {
                            practitioner_id: {string: "Practitioner", type: 'many2one', relation: 'pod.practitioner'},
                        },
                        records: [],
                    },
                    'pod.practitioner': {
                        fields: {},
                        records: [
                            {id: 10, name: "Mario"},
                            {id: 20, name: "Luigi"},
                            {id: 30, name: "Yoshi"}
                        ],
                    },
                };
            },
        });

        QUnit.test('standalone_m2o_avatar_practitioner: legacy view', async function (assert) {
            assert.expect(1);

            const html = "<div class='coucou_test'></div>";
            const view = await createView({
                View: getHtmlView(html, "test"),
                data: this.data,
                model: "foo",
                arch: "<test/>"
            });

            const avatar10 = new StandaloneM2OAvatarPractitioner(view, 10);
            const avatar20 = new StandaloneM2OAvatarPractitioner(view, 20);
            const avatar30 = new StandaloneM2OAvatarPractitioner(view, [30, 'Bowser']);

            await avatar10.appendTo(view.el.querySelector('.coucou_test'));
            await avatar20.appendTo(view.el.querySelector('.coucou_test'));
            await avatar30.appendTo(view.el.querySelector('.coucou_test'));

            assert.deepEqual(
                [...view.el.querySelectorAll('.o_field_many2one_avatar span')].map(el => el.innerText),
                ["Mario", "Luigi", "Bowser"]
            );

            view.destroy();
        });

        QUnit.test('standalone_m2o_avatar_practitioner: Owl view', async function (assert) {
            assert.expect(1);

            class Renderer extends AbstractRendererOwl { }
            Renderer.template = xml`<div class='coucou_test'></div>`;

            const view = await createView({
                View: getOwlView(Renderer, "test"),
                data: this.data,
                model: "foo",
                arch: "<test/>"
            });

            const avatar10 = new StandaloneM2OAvatarPractitioner(view, 10);
            const avatar20 = new StandaloneM2OAvatarPractitioner(view, 20);
            const avatar30 = new StandaloneM2OAvatarPractitioner(view, [30, 'Bowser']);

            await avatar10.appendTo(view.el.querySelector('.coucou_test'));
            await avatar20.appendTo(view.el.querySelector('.coucou_test'));
            await avatar30.appendTo(view.el.querySelector('.coucou_test'));

            assert.deepEqual(
                [...view.el.querySelectorAll('.o_field_many2one_avatar span')].map(el => el.innerText),
                ["Mario", "Luigi", "Bowser"]
            );

            view.destroy();
        });
    });
