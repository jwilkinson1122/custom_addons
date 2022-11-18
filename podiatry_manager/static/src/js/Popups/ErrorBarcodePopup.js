odoo.define('podiatry_manager.ErrorBarcodePopup', function(require) {
    'use strict';

    const ErrorPopup = require('podiatry_manager.ErrorPopup');
    const Registries = require('podiatry_manager.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    // formerly ErrorBarcodePopupWidget
    class ErrorBarcodePopup extends ErrorPopup {
        get translatedMessage() {
            return this.env._t(this.props.message);
        }
    }
    ErrorBarcodePopup.template = 'ErrorBarcodePopup';
    ErrorBarcodePopup.defaultProps = {
        confirmText: _lt('Ok'),
        cancelText: _lt('Cancel'),
        title: _lt('Error'),
        body: '',
        message:
            _lt('The Point of Sale could not find any product, client, employee or action associated with the scanned barcode.'),
    };

    Registries.Component.add(ErrorBarcodePopup);

    return ErrorBarcodePopup;
});
