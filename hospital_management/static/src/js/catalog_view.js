odoo.define('catalog.View', function (require) {
    'use strict';

    var AbstractView = require('web.AbstractView');
    var view_registry = require('web.view_registry');
    var CatalogController = require('catalog.Controller');
    var CatalogModel = require('catalog.Model');
    var CatalogRenderer = require('catalog.Renderer');


    var CatalogView = AbstractView.extend({
        display_name: 'Catalogs',
        icon: 'fa-id-card-o',
        config: {
            Model: CatalogModel,
            Controller: CatalogController,
            Renderer: CatalogRenderer,
        },
        viewType: 'catalog',
        groupable: false,
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            var attrs = this.arch.attrs;
            if (!attrs.catalog_field) {
                throw new Error('Catalog view has not defined "catalog_field" attribute.');
            }
            this.loadParams.catalog_field = attrs.catalog_field;
        },
    });
    view_registry.add('catalog', CatalogView);
    return CatalogView;

});