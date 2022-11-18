odoo.define('podiatry_manager.ConfirmPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('podiatry_manager.AbstractAwaitablePopup');
    const Registries = require('podiatry_manager.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    // formerly ConfirmPopupWidget
    class ConfirmPopup extends AbstractAwaitablePopup {}
    ConfirmPopup.template = 'ConfirmPopup';
    ConfirmPopup.defaultProps = {
        confirmText: _lt('Ok'),
        cancelText: _lt('Cancel'),
        title: _lt('Confirm ?'),
        body: '',
    };

    Registries.Component.add(ConfirmPopup);

    return ConfirmPopup;
});
