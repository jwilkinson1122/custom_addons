odoo.define('catalog.Controller', function (require) {
    'use strict';


    // The role of the Controller is to manage coordination between
    // the Model and the Renderer.


    var AbstractController = require('web.AbstractController')
    var core = require('web.core');
    var qweb = core.qweb;

    var CatalogController = AbstractController.extend({
        

        //when a button in the author card is
        // clicked, the renderer will trigger the event to the controller to make it
        // perform the action.
        custom_events: _.extend({}, AbstractController.prototype.custom_events, {
            'btn_clicked': '_onBtnClicked',
        }),

        //it manages the buttons in the control panel. In our
        // example, we added a button to add new records. To do so, we had to
        // override the renderButtons() method of AbstractController .

        renderButtons: function ($node) {
            if ($node) {
                this.$buttons = $(qweb.render('CatalogView.buttons'));
                this.$buttons.appendTo($node);
                this.$buttons.on('click', 'button', this._onAddButtonClick.bind(this));
            }
        },
        _onBtnClicked: function (ev) {
            this.do_action({
                type: 'ir.actions.act_window',
                name: this.title,
                res_model: this.modelName,
                views: [[false, 'list'], [false, 'form']],
                domain: ev.data.domain,
            });
        },
        _onAddButtonClick: function (ev) {
            this.do_action({
                type: 'ir.actions.act_window',
                name: this.title,
                res_model: this.modelName,
                views: [[false, 'form']],
                target: 'new'
            });
        },

    });

    return CatalogController


})