/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class ProductTemplatePopup extends AbstractAwaitablePopup {
    static template = "pos_manufacturing.ProductTemplatePopup";
    setup() {
        super.setup();
        this.pos = usePos();
    }
    go_back_screen() {
        this.showScreen('ProductScreen');
        this.cancel();
    }
    add_product(ev){
        let self = this;
        this.pos.get_order().add_product(ev);
        let product = ev;
        self.side_prod_list = [];
        
        if (product.sub_products_ids.length > 0){
            product.sub_products_ids.forEach(function (sub_prod) {
                var side_product = self.pos.db.get_product_by_id(sub_prod);
                if (side_product){
                    side_product['image_url'] = `/web/image?model=product.product&field=image_128&id=${sub_prod}&write_date=${side_product.write_date}&unique=1`;
                    self.side_prod_list.push(side_product)
                }
            });
        }
        self.modifier_attribute_list = [];
        if (product.device_laterality){
            let modifier = self.pos.modifier_attribute;
            if(product.modifier_attribute_product_id.length >0){
                product.modifier_attribute_product_id.forEach(function(attr) {
                    var data = self.pos.db.modifier_attribute_by_id[attr]
                    self.modifier_attribute_list.push(data)
                });
            }
            self.pos.modifier_attribute = self.modifier_attribute_list;
            self.pos.side_prod_list = self.side_prod_list;
            $('.product-list').hide();
            // $('.products-widget-control').hide();
            $('.products-widget-control').addClass('d-none');
            $('.product-list').addClass('d-none');
            $('#modifier-product-name').text(product.display_name);
            $('.modifiers-list').show()
        }
        this.cancel();  


    }
    get imageUrl() {
        const product = this.props.product;
        return `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
    }
    get pricelist() {
        const current_order = this.pos.get_order();
        if (current_order) {
            return current_order.pricelist;
        }
        return this.pos.default_pricelist;
    }
    get price() {
        const formattedUnitPrice = this.env.utils.formatCurrency(
            this.props.product.get_price(this.pricelist, 1),
            'Product Price'
        );
        if (this.props.product.to_weight) {
            return `${formattedUnitPrice}/${
                this.env.pos.units_by_id[this.props.product.uom_id[0]].name
            }`;
        } else {
            return formattedUnitPrice;
        }
    }

    renderElement() {
        var el_str  = QWeb.render(this.env.template, {widget: this});
        var el_node = document.createElement('div');
            el_node.innerHTML = el_str;
            el_node = el_node.childNodes[1];
        if(this.el && this.el.parentNode){
            this.el.parentNode.replaceChild(el_node,this.el);
        }
        this.el = el_node;
        var list_container = el_node.querySelector('.productt-list');
        for(var i = 0, len = this.product_list.length; i < len; i++){
            var product_node = this.render_product(this.product_list[i]);
            product_node.addEventListener('click',this.click_product_handler);
            list_container.appendChild(product_node);
        }
    }
}