odoo.define('dv_pos_product_info_popup.ProductInfoPopup', function(require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { useState } = owl.hooks;
    
    class ProductInfoPopup extends AbstractAwaitablePopup {
     constructor() {
     super(...arguments);
     useListener('click-product', this._clickProduct);
     }
      async _clickProduct(event) {
            console.log(event)
        }
     }
 
     //Create products popup
    ProductInfoPopup.template = 'ProductInfoPopup';
    Registries.Component.add(ProductInfoPopup);
    return ProductInfoPopup;
 });