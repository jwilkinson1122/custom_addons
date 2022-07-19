odoo.define('pos_product_addons.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;


    models.load_fields('product.product', ['addon_ids', 'has_addons']);

    var _super_pos = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        get_addon_list: function (product_id) {
            // Calls once clicks on the product and shows its add-ons.
            var self = this;
            $('.addon-contents').empty();
            var product = self.db.get_product_by_id(product_id);
            var element = [];
            if (product.addon_ids.length) {
                var $addonpane = $('.addonpane');
                if (this.env.isMobile){
                    $('.product-list-container').css("width", "70%");
                    $addonpane.css("visibility", "visible");
                    $addonpane.css("width", "30%");

                }else{
                    $('.product-list-container').css("width", "80%");
                    $addonpane.css("visibility", "visible");
                    $addonpane.css("width", "13.1%");
                }
                var display_name = '('+product.display_name+')'
                $('.sub-head').text(display_name).show('fast');
                for (var item = 0; item < product.addon_ids.length; item++) {
                    var product_obj = self.db.get_product_by_id([product.addon_ids[item]]);
                    if (product_obj) {
                        element = product_obj.display_name;
                        $('.addons-table').append(
                            '<tr class="addon-contents" class="row" style="width: 100%;">' +
                            '<td class="addons-item" style="width: 100%;" data-addon-id=' + product_obj.id + '> ' +
                            '<div class="addons-product" style="display: inline-block; width: 80%;">' + element + '</div>' +
                            '</div></td>' +
                            '</tr>');
                    }
                }
            } else {
                self.hide_addons()
            }

        },
        hide_addons: function () {
            var $layout_table = $('.product-list-container');
            $layout_table.removeAttr("width");
            $layout_table.css("width", "100%");
            $('.addonpane').css("visibility", "hidden");
        },
        sync_from_server: function(table, table_orders, order_ids) {
            var self = this;
            var ids_to_remove = this.db.get_ids_to_remove_from_server();
            var orders_to_sync = this.db.get_unpaid_orders_to_sync(order_ids);
            if (orders_to_sync.length) {
                var items_list = orders_to_sync[0].data.lines[0][2].addon_items
                if (items_list.length == 0){
                    this.set_synch('connecting', orders_to_sync.length);
                    this._save_to_server(orders_to_sync, {'draft': true}).then(function (server_ids) {
                        server_ids.forEach(server_id => self.update_table_order(server_id, table_orders));
                        if (!ids_to_remove.length) {
                            self.set_synch('connected');
                        } else {
                            self.remove_from_server_and_set_sync_state(ids_to_remove);
                        }
                    }).catch(function(reason){
                        self.set_synch('error');
                    }).finally(function(){
                        self.clean_table_transfer(table);
                    });
                }
            } else {
                if (ids_to_remove.length) {
                    self.remove_from_server_and_set_sync_state(ids_to_remove);
                }
                self.clean_table_transfer(table);
            }
    },
    });


    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            _super_orderline.initialize.call(this, attr, options);
            this.addon_items = this.addon_items || [];
        },

        init_from_JSON: function (json) {
            _super_orderline.init_from_JSON.apply(this, arguments);
            this.addon_items = json.addon_items || [];

        },
        export_as_JSON: function () {
            var json = _super_orderline.export_as_JSON.apply(this, arguments);
            json.addon_items = this.addon_items || [];
            return json;
        },
        can_be_merged_with: function (orderline) {
            if (orderline.product.has_addon) {
                return false;
            } else {
                return _super_orderline.can_be_merged_with.apply(this, arguments);
            }
        },
        //used to create a json of the ticket, to be sent to the printer

        export_for_printing: function(){

        return {
            id: this.id,
            quantity:           this.get_quantity(),
            unit_name:          this.get_unit().name,
            price:              this.get_unit_display_price(),
            discount:           this.get_discount(),
            product_name:       this.get_product().display_name,
            product_name_wrapped: this.generate_wrapped_product_name(),
            price_lst:          this.get_lst_price(),
            display_discount_policy:    this.display_discount_policy(),
            price_display_one:  this.get_display_price_one(),
            price_display :     this.get_display_price(),
            price_with_tax :    this.get_price_with_tax(),
            price_without_tax:  this.get_price_without_tax(),
            price_with_tax_before_discount:  this.get_price_with_tax_before_discount(),
            tax:                this.get_tax(),
            product_description:      this.get_product().description,
            product_description_sale: this.get_product().description_sale,
            orderline_id :          this.id,
        };
    },

    get_base_price:    function(){
        var rounding = this.pos.currency.rounding;
        var total_addon_price = 0.0;
        if (this.addon_items.length) {
            _(this.addon_items).each(function(addon) {
                total_addon_price += addon.addon_count * addon.addon_price_without
            });
        }
        return round_pr(((this.get_unit_price() * this.get_quantity()) + total_addon_price) * (1 - this.get_discount()/100) , rounding);
    },

    get_price_with_tax: function(){
        var rounding = this.pos.currency.rounding;
        var total_addon_price = 0.0;
        if (this.addon_items.length) {
            _(this.addon_items).each(function(addon) {
                total_addon_price += addon.addon_count * addon.addon_price_with
            });
        }
        return this.get_all_prices().priceWithTax;
    },

    get_all_prices: function(){
        var self = this;
        var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
        var taxtotal = 0;

        var product =  this.get_product();
        var taxes_ids = this.tax_ids || product.taxes_id;
        taxes_ids = _.filter(taxes_ids, t => t in this.pos.taxes_by_id);
        var taxes =  this.pos.taxes;
        var taxdetail = {};
        var product_taxes = [];

        _(taxes_ids).each(function(el){
            var tax = _.detect(taxes, function(t){
                return t.id === el;
            });
            product_taxes.push.apply(product_taxes, self._map_tax_fiscal_position(tax, self.order));
        });
        product_taxes = _.uniq(product_taxes, function(tax) { return tax.id; });
        var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
        var all_taxes_before_discount = this.compute_all(product_taxes, this.get_unit_price(), this.get_quantity(), this.pos.currency.rounding);
        _(all_taxes.taxes).each(function(tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = tax.amount;
        });
        if(self.addon_items && self.addon_items.length != 0){
            var tax_amount = 0.0
            var receipttax = {}
            var tax_compute = this.compute_all(product_taxes, self.product.lst_price, this.get_quantity(), this.pos.currency.rounding);
            _(tax_compute.taxes).each(function(tax) {
                tax_amount += tax.amount;
                receipttax[tax.id] = tax.amount;
            });

            var difference = taxtotal - tax_amount;
            taxtotal = taxtotal - difference
            var total_addon_tax = 0.0
            _(self.addon_items).each(function(addon) {
                if (addon.tax) {
                    var addon_taxes = addon.tax
                    var tax_index = 0;
                    taxes.forEach(function (item, index) {
                      if (item.id == addon_taxes){
                        tax_index = index;
                      }
                    });
                    var is_include = taxes[tax_index].include_base_amount;
                    if (is_include==true){
                        var addon_tax = addon.total_without - addon.total_without_including;
                    }else{
                        var addon_tax = addon.total_with - addon.total_without;
                    }
                    total_addon_tax += addon_tax;
                    console.log(total_addon_tax,'total_addon_tax')
                    receipttax[addon.tax] = round_pr(addon_tax, self.pos.currency.rounding);
                }
            });
            _(tax_compute.taxes).each(function(tax) {
                receipttax[tax.id] += tax.amount;
            });
            taxtotal += round_pr(total_addon_tax, self.pos.currency.rounding)
            taxdetail = receipttax
        }
        return {
            "priceWithTax": all_taxes.total_included,
            "priceWithoutTax": all_taxes.total_excluded,
            "priceSumTaxVoid": all_taxes.total_void,
            "priceWithTaxBeforeDiscount": all_taxes_before_discount.total_included,
            "tax": taxtotal,
            "taxDetails": taxdetail,
        };
},

        get_addon_uom: function (id) {
            for (var i = 0; i <= this.addon_items.length; i++) {
                if (this.addon_items[i]['addon_id'] == id) {
                    return this.addon_items[i]['addon_uom']
                }
            }

        }
    });

    var _super = models.Order;
    models.Order = models.Order.extend({
        get_total_without_tax: function() {
        return round_pr(this.orderlines.reduce((function(sum, orderLine) {
            var total_addon_price = 0.0;
            if (orderLine.addon_items.length) {
                _(orderLine.addon_items).each(function(addon) {
                    var taxes_list =  self.posmodel.taxes;
                    var addon_tax_list = addon.tax
                    var tax_indexs = 0;
                    taxes_list.forEach(function (items, index) {
                      if (items.id == addon_tax_list){
                        tax_indexs = index;
                      }
                    });
                    var is_includes = taxes_list[tax_indexs].include_base_amount;
                    if (is_includes==true){
                        var addon_price_withouts = addon.addon_price_without_including;
                    }else{
                        var addon_price_withouts = addon.addon_price_without;
                    }
                    total_addon_price += addon.addon_count * addon_price_withouts
                });
            }
            return sum + total_addon_price + orderLine.get_price_without_tax();
        }), 0), this.pos.currency.rounding);
    },
    });

    });

