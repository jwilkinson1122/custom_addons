odoo.define('podiatry_manager.tour.TextAreaPopupTourMethods', function (require) {
    'use strict';

    const { createTourMethods } = require('podiatry_manager.tour.utils');

    class Do {
        inputText(val) {
            return [
                {
                    content: `input text '${val}'`,
                    trigger: `.modal-dialog .popup-textarea textarea`,
                    run: `text ${val}`,
                },
            ];
        }
        clickConfirm() {
            return [
                {
                    content: 'confirm text input popup',
                    trigger: '.modal-dialog .confirm',
                },
            ];
        }
    }

    class Check {
        isShown() {
            return [
                {
                    content: 'text input popup is shown',
                    trigger: '.modal-dialog .popup-textarea',
                    run: () => {},
                },
            ];
        }
    }

    return createTourMethods('TextAreaPopup', Do, Check);
});
