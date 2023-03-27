odoo.define('catalog.Renderer', function (require) {
    'use strict';


    // The role of the Renderer is to manage the DOM elements for
    // the view. Every view can render data in a different way. In the renderer,
    // you can get the state of the model in a state variable.




    var AbstractRenderer = require('web.AbstractRenderer');
    var core = require('web.core');
    var qweb = core.qweb;


    var CatalogRenderer = AbstractRenderer.extend({
        events: _.extend({}, AbstractRenderer.prototype.events, {
            'click .o_primay_button': '_onClickButton',
        }),
        
        _render: function () {
            var self = this;
            this.$el.append(qweb.render('ViewCatalog', {
                'groups': this.state,
            }));
            var custom_view = qweb.render('ViewCatalog', {'groups': this.state })
            $(custom_view).prependTo(self.$el);
            return custom_view;
        },
        _onClickButton: function (ev) {
            ev.preventDefault();
            var target = $(ev.currentTarget);
            var group_id = target.data('group');
            var children_ids = _.map(this.state[group_id].children, function (group_id) {
                    return group_id.id;
                });
            this.trigger_up('btn_clicked', {'domain': [['id', 'in', children_ids]]
            });
        }
    })
    return CatalogRenderer;

})