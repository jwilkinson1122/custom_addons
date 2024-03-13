/** @odoo-module */

import { Order, Orderline} from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import {
    formatFloat,
    roundDecimals as round_di,
    roundPrecision as round_pr,
    floatIsZero,
} from "@web/core/utils/numbers";

patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
    },
    init_from_JSON(json) {
        var self = this
        super.init_from_JSON(...arguments);
        this.has_option = json.has_option;
        this.is_option = json.is_option || false;
        this.option = json.option || null
        this.Options_temp = json.Options_temp || []
        this.Options = json.Options || []
        this.Options.forEach(function (each, key) {
            var orderline = new Orderline({}, {
                pos: self.pos,
                order: self.order,
                id: each.id,
                product: self.pos.db.get_product_by_id(each.product_id),
                price: each.price,
            });
            orderline.set_quantity(each.quantity)
            self.Options_temp[key] = orderline
        });
    },
    export_as_JSON() {
        var res = super.export_as_JSON(...arguments);
        res['has_option'] = this.has_option;
        res['pod_has_option'] = this.has_option;
        res['is_option'] = this.is_option || false;
        res['pod_is_option'] = this.is_option || false;
        return res
    },
    get_has_option() {
        return this.has_option
    },
    set_has_option(has_option) {
        this.has_option = has_option
    },
    export_for_printing() {
        let result = super.export_for_printing(...arguments);
        result['has_option'] = this.has_option || false;
        result['Options'] = this.Options || []
        result['is_option'] = this.is_option || false

        return result;
    },
    get_option() {
        return this.option || []
    },
    set_option(option) {
        this.option = option
    },
    get_options() {
        return this.Options || []
    },
    set_options(Options) {
        if (!this.Options) {
            this.Options = [Options]
        } else {
            this.Options.push(Options)
        }
    },
    get_options_temp() {
        return this.Options_temp || []
    },
    set_options_temp(Options) {
        if (!this.Options_temp) {
            this.Options_temp = [Options]
        } else {
            this.Options_temp.push(Options)
        }
    },
    can_be_merged_with(orderline) {
        if (this.pos.config.pod_enable_options && this.pos.config.pod_allow_same_product_different_qty) {
            if (this.has_option) {
                return false
            } else if (!this.is_option) {
                if (orderline.product.pod_option_ids.length){
                    return false
                }else{
                    return super.can_be_merged_with(orderline);
                }
            } else {
                // super.can_be_merged_with.apply(this, arguments);
                return false
            }
        } else if (!this.is_option) {
            return super.can_be_merged_with(orderline);
        } else {
            return false
        }
    },
    /**
     * override
     */
    getDisplayClasses() {
        return {
            ...super.getDisplayClasses(),
            "pod-is-option": this.is_option ? this.is_option : false,
        };
    },
    options_can_be_merged_with(orderline) {
        var price = parseFloat(round_di(this.price || 0, this.pos.dp['Product Price']).toFixed(this.pos.dp['Product Price']));
        var order_line_price = orderline.product.get_price(this.order.pricelist, this.get_quantity());
        order_line_price = this.compute_fixed_price(order_line_price);
        if (this.get_product().id !== orderline.get_product().id) {    //only orderline of the same product can be merged
            return false;
        } else if (!this.get_unit() || !this.get_unit().is_pos_groupable) {
            return false;
        } else if (this.get_discount() > 0) {             // we don't merge discounted orderlines
            return false;
        } else if (this.product.tracking == 'lot' && (this.pos.picking_type.use_create_lots || this.pos.picking_type.use_existing_lots)) {
            return false;
        } else if (this.description !== orderline.description) {
            return false;
        } else if (this.get_customer_note() !== this.get_customer_note()) {
            return false;
        } else if (this.refunded_orderline_id) {
            return false;
        } else {
            return true;
        }
    },

    getDisplayData() {
        let res = super.getDisplayData();
        res['has_option'] = this.has_option;
        res['Options'] = this.Options;
        res['is_option'] = this.is_option;
        
        return res
    }
});
patch(Order.prototype, {
    constructor(obj, options) {
        super.constructor(obj, options)
        if (this.get_orderlines() && this.get_orderlines().length) {
            let parentline = false
            for (let line of this.get_orderlines()) {
                if (line.has_option) {
                    parentline = line
                } else {
                    var dic = {
                        quantity: line.get_quantity(),
                        quantityStr: line.quantityStr,
                        price_unit: line.get_unit_price(),
                        price_subtotal: line.get_price_without_tax(),
                        price_subtotal_incl: line.get_price_with_tax(),
                        discount: line.get_discount(),
                        product_id: line.product.id,
                        product: line.get_product(),
                        unit: line.product.get_unit().name,
                        tax_ids: [[6, false, this.get_applicable_taxes().map(line.get_applicable_taxes(), function (tax) { return tax.id; })]],
                        id: line.id,
                        description: line.description,
                        full_product_name: line.get_full_product_name(),
                        price_extra: line.get_price_extra(),
                        price_display: line.get_display_price(),
                        customer_note: line.get_customer_note(),
                        refunded_orderline_id: line.refunded_orderline_id,
                        price_manually_set: line.price_manually_set,
                        parent_orderline_id: parentline.id,
                        parent_orderline: parentline,
                    }
                    if (parentline) {
                        if (line.is_option) {
                            parentline.set_options_temp(line)
                            parentline.set_options(dic)
                        }
                    }
                }
            }
        }
    },
    removeOrderline(line) {
        var self = this;
        if (line.Options) {
            line.Options.forEach(function (each_option) {
                if (each_option && each_option.id) {
                    self.removeOrderline(self.get_orderline(each_option.id));
                }
            })
        }
        var res = super.removeOrderline(line)
        return res
    },
    export_as_JSON() {
        console.log('JSON');
        var self = this;
        const json = super.export_as_JSON(...arguments);

        var orderLines = []

        for (var i = 0; i < self.get_orderlines().length; i++) {
            var item = self.get_orderlines()[i]
            if (item) {
                if (item.Options) {
                    item['Options'] = item.Options
                }
                if (item.is_option) {
                    item['is_option'] = item.is_option
                }
                orderLines.push([0, 0, item.export_as_JSON()]);
            }
        }
        if (orderLines && orderLines.length > 0) {
            json['lines'] = orderLines;
        }
        return json
    },
    get_last_orderline() {
        const regularLines = this.get_orderlines
            .apply(this, arguments)
            .filter((line) => !line.is_option);
        return regularLines[regularLines.length - 1];
    },

    async add_option_product(product, options) {
        this.assert_editable();
        var self = this;
        options = options || {};
        var SelectedOrderline = this.get_selected_orderline()
        SelectedOrderline.set_has_option(true)
        var line = new Orderline(
            { env: this.env },
            {
                pos: this.pos,
                order: this,
                product: product,
            }
        );
        line.is_option = true
        this.fix_tax_included_price(line);
        this.set_orderline_options(line, options);
        line.set_full_product_name();
        var product_ids = []
        var to_merge_orderline;
        if (SelectedOrderline.get_options_temp() && SelectedOrderline.get_options_temp().length) {
            for (var i = 0; i < SelectedOrderline.get_options_temp().length; i++) {
                if (SelectedOrderline.get_options_temp().at(i).options_can_be_merged_with(line) && options.merge !== false) {
                    to_merge_orderline = SelectedOrderline.get_options_temp().at(i)
                }
            }
        }
        if (to_merge_orderline) {
            to_merge_orderline.merge(line);
            var dic1 = {
                quantity: to_merge_orderline.get_quantity(),
                quantityStr: to_merge_orderline.quantityStr,
                price_unit: to_merge_orderline.get_unit_price(),
                price_subtotal: to_merge_orderline.get_price_without_tax(),
                price_subtotal_incl: to_merge_orderline.get_price_with_tax(),
                discount: to_merge_orderline.get_discount(),
                product_id: product.id,
                product: product,
                unit: to_merge_orderline.product.get_unit().name,
                tax_ids: [[6, false, this.get_selected_orderline().get_applicable_taxes().map((tax) => tax.id)]],
                id: to_merge_orderline.id,
                price_display: to_merge_orderline.get_display_price(),
                description: to_merge_orderline.description,
                full_product_name: to_merge_orderline.get_full_product_name(),
                price_extra: to_merge_orderline.get_price_extra(),
                customer_note: to_merge_orderline.get_customer_note(),
                refunded_orderline_id: to_merge_orderline.refunded_orderline_id,
                price_manually_set: to_merge_orderline.price_manually_set,
                parent_orderline_id: SelectedOrderline.id,
                parent_orderline: SelectedOrderline,
            }
            SelectedOrderline.get_options_temp().forEach(function (eachoption, key) {
                if (eachoption.product.id == dic1.product.id) {
                    SelectedOrderline.Options[key] = dic1
                }
            });

            SelectedOrderline.set_option(to_merge_orderline)
            if (self.get_orderline(to_merge_orderline.id)) {
                self.get_orderline(to_merge_orderline.id).set_quantity(to_merge_orderline.quantity)
            }

        } else {
            var dic = {
                quantity: line.get_quantity(),
                quantityStr: line.quantityStr,
                price_unit: line.get_unit_price(),
                price_subtotal: line.get_price_without_tax(),
                price_subtotal_incl: line.get_price_with_tax(),
                discount: line.get_discount(),
                product_id: product.id,
                product: product,
                unit: line.product.get_unit().name,
                tax_ids: [[6, false, this.get_selected_orderline().get_applicable_taxes().map((tax) => tax.id)]],
                id: line.id,
                description: line.description,
                full_product_name: line.get_full_product_name(),
                price_extra: line.get_price_extra(),
                price_display: line.get_display_price(),
                customer_note: line.get_customer_note(),
                refunded_orderline_id: line.refunded_orderline_id,
                price_manually_set: line.price_manually_set,
                parent_orderline_id: SelectedOrderline.id,
                parent_orderline: SelectedOrderline,
            }
            SelectedOrderline.set_option(line);
            SelectedOrderline.set_options_temp(line)
            SelectedOrderline.set_options(dic);
            line['pod_option_parent'] = SelectedOrderline
            self.pos.get_order().add_orderline(line)
        }
        self.pos.get_order().select_orderline(SelectedOrderline);


        // if (options.draftPackLotLines) {
        //     SelectedOrderline.setPackLotLines(options.draftPackLotLines);
        // }
    }
});
