odoo.define('catalog.Model', function (require) {
    'use strict';

    // The role of the Model is to hold the state of the view. It sends an
    // RPC request to the server for the data, and then passes the data to the
    // controller and renderer.


    var AbstractModel = require('web.AbstractModel')
    var CatalogModel = AbstractModel.extend({



        get: function () {
            return this.data;
        },

        //When view is being initialized, it calls load method to fetch data
        load: function (params) {
            console.log("load called")
            this.modelName = params.modelName;
            this.domain = params.domain;
            this.catalog_field = params.catalog_field;
            return this._fetchData();
        },

        //When search conditions are changed and view needs a new state
        reload: function (handle, params) {
            if ('domain' in params) {
                this.domain = params.domain;
            }
            return this._fetchData();
        },
        _fetchData: function () {
            var self = this;
            return this._rpc({
                model: this.modelName,
                method: 'get_catalog_data',
                kwargs: {
                    domain: this.domain,
                    catalog_field: this.catalog_field,
                }
            }).then(function (result) {
                self.data = result
            })
        }
    });

    return CatalogModel;
})