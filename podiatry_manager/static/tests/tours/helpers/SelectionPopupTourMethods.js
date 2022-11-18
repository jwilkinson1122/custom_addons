odoo.define('podiatry_manager.tour.SelectionPopupTourMethods', function (require) {
    'use strict';

    const { createTourMethods } = require('podiatry_manager.tour.utils');

    class Do {
        clickItem(name) {
            return [
                {
                    content: `click selection '${name}'`,
                    trigger: `.selection-item:contains("${name}")`,
                },
            ];
        }
    }

    class Check {
        hasSelectionItem(name) {
            return [
                {
                    content: `selection popup has '${name}'`,
                    trigger: `.selection-item:contains("${name}")`,
                    run: () => {},
                },
            ];
        }
        isShown() {
            return [
                {
                    content: 'selection popup is shown',
                    trigger: '.modal-dialog .popup-selection',
                    run: () => {},
                },
            ];
        }
    }

    return createTourMethods('SelectionPopup', Do, Check);
});
