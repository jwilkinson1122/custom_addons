odoo.define('podiatry_pos_modifier.ProductProduct', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');

    class ProductProduct extends PosComponent {
        /**
         * For accessibility, pressing <space> should be like clicking the product.
         * <enter> is not considered because it conflicts with the barcode.
         *
         * @param {KeyPressEvent} event
         */

        constructor() {
            super(...arguments);
            useListener('click-product-template', this.add_product);
        }


        add_product() {
            let self = this;
            this.env.pos.get_order().add_product(this.props.product);
            let product = self.props.product;
            self.side_prod_list = [];

            if (product.sub_products_ids.length > 0) {
                product.sub_products_ids.forEach(function (sub_prod) {
                    var side_product = self.env.pos.db.get_product_by_id(sub_prod);

                    side_product['image_url'] = `/web/image?model=product.product&field=image_128&id=${sub_prod}&write_date=${side_product.write_date}&unique=1`;
                    self.side_prod_list.push(side_product)
                });
            }
            self.modifier_attribute_list = [];
            if (product.laterality_display) {
                let modifier = self.env.pos.modifier_attribute;
                if (product.modifier_attribute_product_id.length > 0) {
                    product.modifier_attribute_product_id.forEach(function (attr) {
                        var data = self.env.pos.db.modifier_attribute_by_id[attr]
                        self.modifier_attribute_list.push(data)
                    });
                }
                self.env.pos.modifier_attribute = self.modifier_attribute_list;
                self.env.pos.side_prod_list = self.side_prod_list;
                $('.product-list').hide();
                $('.products-widget-control').hide();
                $('#modifier-product-name').text(product.display_name);
                $('.modifiers-list').show()
            }
            this.trigger('close-popup');
        }
        get imageUrl() {
            const product = this.props.product;
            return `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
        }
        get pricelist() {
            const current_order = this.env.pos.get_order();
            if (current_order) {
                return current_order.pricelist;
            }
            return this.env.pos.default_pricelist;
        }
        get price() {
            const formattedUnitPrice = this.env.pos.format_currency(
                this.props.product.get_price(this.pricelist, 1),
                'Product Price'
            );
            if (this.props.product.to_weight) {
                return `${formattedUnitPrice}/${this.env.pos.units_by_id[this.props.product.uom_id[0]].name
                    }`;
            } else {
                return formattedUnitPrice;
            }
        }

        renderElement() {
            var el_str = QWeb.render(this.env.template, { widget: this });
            var el_node = document.createElement('div');
            el_node.innerHTML = el_str;
            el_node = el_node.childNodes[1];
            if (this.el && this.el.parentNode) {
                this.el.parentNode.replaceChild(el_node, this.el);
            }
            this.el = el_node;
            var list_container = el_node.querySelector('.product-list');
            for (var i = 0, len = this.product_list.length; i < len; i++) {
                var product_node = this.render_product(this.product_list[i]);
                product_node.addEventListener('click', this.click_product_handler);
                list_container.appendChild(product_node);
            }
        }
    }
    ProductProduct.template = 'ProductProduct';

    Registries.Component.add(ProductProduct);

    return ProductProduct;
});
