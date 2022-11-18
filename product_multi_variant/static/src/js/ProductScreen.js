odoo.define('product_multi_variant.ProductScreen', function(require) {
    'use strict';

    var ProductScreen = require('podiatry_manager.ProductScreen');
    const Registries = require('podiatry_manager.Registries');
    const NumberBuffer = require('podiatry_manager.NumberBuffer');
    var models = require('podiatry_manager.models');
    var rpc = require('web.rpc');

    models.load_models([
    {   model: 'variants.tree',
        fields: ["product_active", "value", "attribute", "variants_id", "extra_price"],
        loaded: function(self, variants_tree)
        {   self.variant_tree = variants_tree;
            _.each(variants_tree, function(item)
            {   self.item = item;
            });
        }
    },{    model: 'product.attribute.value',
            fields: ["id", "name"],
            loaded: function(self,values)
            {   self.values = values;
            }
      }]);

    var super_models = models.PosModel.prototype.models;
    models.load_fields('product.product', 'product_variants');
    models.load_fields('product.product', 'variant_line_ids');

    const ProductScreenExtend = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
            }

            async _clickProduct(event) {
                if (!this.currentOrder) {
                    this.env.pos.add_new_order();
                }
            const product = event.detail;
            var variant_product = ''
                await rpc.query({
                    model: 'variants.tree',
                    method: 'search_read',
                    fields: ['extra_price','attribute','value', 'variants_id'],
                    args: [[['variants_id','=',event.detail.product_tmpl_id]]]
                    }).then(function (data) {
                        variant_product = data

                });
                var li=[]
                for(var i=0; i<variant_product.length; ++i) {
                    variant_product[i].value.forEach(function (field) {
                        li.push(field)
                    });

                }

                var variant_details = ''
                await rpc.query({
                        model: 'product.attribute.value',
                        method: 'search_read',
                        fields: ['name'],
                        domain: [['id', 'in', li]],
                        }).then(function (result) {
                        variant_details = result
                    });

                const options = await this._getAddProductOptions(product);

                // Do not add product if options is undefined.
                if (!options) return;
                // Add the product after having the extra information.
                this.currentOrder.add_product(product, options);
                NumberBuffer.reset();
                if(product.product_variants)
                    this.showPopup('ProductsPopup',{
                        title:  product.display_name,
                        products: variant_product,
                        product_tmpl_id: event.detail.id,
                        variant_details: variant_details,
                    });
            }


        };
    Registries.Component.extend(ProductScreen, ProductScreenExtend);
    return ProductScreen;

});