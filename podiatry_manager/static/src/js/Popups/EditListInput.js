odoo.define('podiatry_manager.EditListInput', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class EditListInput extends PosComponent {
        onKeyup(event) {
            if (event.key === "Enter" && event.target.value.trim() !== '') {
                this.trigger('create-new-item');
            }
        }
    }
    EditListInput.template = 'EditListInput';

    Registries.Component.add(EditListInput);

    return EditListInput;
});
