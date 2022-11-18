odoo.define('podiatry_manager.CategoryBreadcrumb', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class CategoryBreadcrumb extends PosComponent {}
    CategoryBreadcrumb.template = 'CategoryBreadcrumb';

    Registries.Component.add(CategoryBreadcrumb);

    return CategoryBreadcrumb;
});
