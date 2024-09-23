/** @odoo-module */
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, onMounted } from "@odoo/owl";

export class PosOrderCustomizationPopup extends AbstractAwaitablePopup {
    static template = "pod_pos_order_customizations.PosOrderCustomizationPopup";

    static defaultProps = { 
        title: 'Confirm ?', 
        value:'' 
    };

    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        if (this.props.product)
            this.props.image_url = this.pod_get_product_image_url(this.props.product);
        onMounted(this.onMounted);
    }

    onMounted(){
        $('.tab-link:first-child').addClass('text-primary')
    }

    pod_add_customization(event) {
        // Call the parent method if necessary
        if (super.pod_add_customization) {
            super.pod_add_customization(event);
        }

        // Collect all checked customizations
        var all_checked_customization = $('.pod_checked_customization:checked');
        var customization_list = [];
        all_checked_customization.each(function(idx, element) {
            customization_list.push($(element).data('id'));
        });

        // Update the customization IDs on the line
        var line = this.props.line;
        line.pod_customization_ids = customization_list;

        // Set line price and extra price flag if there are available customizations
        var line_price = line.price;
        if (customization_list.length) {
            line.is_extra_price_set = false;
        }
        line.set_unit_price(line_price);

        // Save the order to the database if applicable
        if (this.env && this.env.pos && this.env.pos.get_order()) {
            this.env.pos.get_order().save_to_db();
        }

        // Call the cancel method
        this.cancel();
    }

    pod_change_tab(event){
        var content_div_id = $(event.target).data('id');
        if(content_div_id){
            $('.tab-content').removeClass('current');
            $('.tab-link').removeClass('current');
            $('.tab-link').removeClass('text-primary');
            $(event.currentTarget).addClass('text-primary');
            $(content_div_id).addClass('current');
        }
    }

    pod_get_product_image_url(product){
        return window.location.origin + '/web/image?model=product.product&field=image_128&id=' + product.id;
    }
}