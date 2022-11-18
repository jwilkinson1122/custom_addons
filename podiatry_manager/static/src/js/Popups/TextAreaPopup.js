odoo.define('podiatry_manager.TextAreaPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('podiatry_manager.AbstractAwaitablePopup');
    const Registries = require('podiatry_manager.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    // formerly TextAreaPopupWidget
    // IMPROVEMENT: This code is very similar to TextInputPopup.
    //      Combining them would reduce the code.
    class TextAreaPopup extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);
            this.state = useState({ inputValue: this.props.startingValue });
            this.inputRef = useRef('input');
        }
        mounted() {
            this.inputRef.el.focus();
        }
        getPayload() {
            return this.state.inputValue;
        }
    }
    TextAreaPopup.template = 'TextAreaPopup';
    TextAreaPopup.defaultProps = {
        confirmText: _lt('Ok'),
        cancelText: _lt('Cancel'),
        title: '',
        body: '',
    };

    Registries.Component.add(TextAreaPopup);

    return TextAreaPopup;
});
