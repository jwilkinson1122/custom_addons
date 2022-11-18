odoo.define('podiatry_manager.CategorySimpleButton', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class CategorySimpleButton extends PosComponent {}
    CategorySimpleButton.template = 'CategorySimpleButton';

    Registries.Component.add(CategorySimpleButton);

    return CategorySimpleButton;
});
