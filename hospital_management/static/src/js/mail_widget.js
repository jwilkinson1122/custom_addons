odoo.define('email_widget', function (require) {
    "use strict";


    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');

    var mailField = AbstractField.extend({

        tagName: 'span',
        supportedFieldTypes: ['char'],

        init: function () {
            
            this._super.apply(this, arguments);
            this._setValue("hello@example.com")
            console.log('init func called')
            //Constructor Method
        },
        // start: function() {
        //     console.log('start func called')
            
        // },

        _renderEdit: function () {
            console.log('_renderEdit func called')
            console.log(this.value)
            var validRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
            if (this.value.match(validRegex)) {
                this.$el.append($("<div class='c-valid'>Valid Email Address!</div>"));
            }
            else {
                this.$el.append("<div class='c-valid'>Valid Email Address!</div>");
            }


        },
        _renderReadonly: function () {
            console.log('renderReadonly func called')
        },





    })


    fieldRegistry.add('char_mail', mailField);


    return {
        mailField: mailField,
    };





})