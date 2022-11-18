odoo.define('podiatry_manager.ProductList', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class ProductList extends PosComponent {}
    ProductList.template = 'ProductList';

    Registries.Component.add(ProductList);

    return ProductList;
});
