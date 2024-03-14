/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    setup() {
        super.setup()
        setTimeout(() => {

            var owl = $('.owl-carousel');
            owl.owlCarousel({
                loop: false,
                nav: true,
                margin: 10,
                responsive: {
                    0: {
                        items: 1
                    },
                    600: {
                        items: 3
                    },
                    960: {
                        items: 5
                    },
                    1200: {
                        items: 6
                    }
                }
            });
            owl.on('mousewheel', '.owl-stage', function (e) {
                if (e.originalEvent.wheelDelta > 0) {
                    owl.trigger('next.owl');
                } else {
                    owl.trigger('prev.owl');
                }
                e.preventDefault();
            });
        }, 20);
    },
    onMounted() {
        super.onMounted()
        if(this && this.pos && this.pos.pos_theme_settings_data && this.pos.pos_theme_settings_data[0] && this.pos.pos_theme_settings_data[0].pod_cart_position && this.pos.pos_theme_settings_data[0].pod_cart_position == 'right_side'){
            $('.rightpane').insertBefore($('.leftpane'));
        }
        if(this && this.pos && this.pos.pos_theme_settings_data && this.pos.pos_theme_settings_data[0] && this.pos.pos_theme_settings_data[0].pod_action_button_position && this.pos.pos_theme_settings_data[0].pod_action_button_position == 'bottom'){
            $('.product-screen').addClass('pod_control_button_bottom')
        }else if(this && this.pos && this.pos.pos_theme_settings_data && this.pos.pos_theme_settings_data[0] && this.pos.pos_theme_settings_data[0].pod_action_button_position && this.pos.pos_theme_settings_data[0].pod_action_button_position == 'left_side'){
            $('.product-screen').addClass('pod_control_button_left')
        }else if(this && this.pos && this.pos.pos_theme_settings_data && this.pos.pos_theme_settings_data[0] && this.pos.pos_theme_settings_data[0].pod_action_button_position && this.pos.pos_theme_settings_data[0].pod_action_button_position == 'right_side'){
            $('.product-screen').addClass('pod_control_button_right')
        }


        if (window.innerWidth <= 767.98) {
            if (this.pos.pos_theme_settings_data[0].pod_mobile_start_screen == "product_screen") {
                $(".leftpane").css("display", "none");
                $(".rightpane").css("display", "flex");
                $(".pod_cart_management").css("display", "none");
                $(".pod_product_management").removeClass("hide_cart_screen_show");
                $(".pod_product_management").css("display", "flex");
            }
            if (this.pos.pos_theme_settings_data[0].pod_mobile_start_screen == "cart_screen") {
                $(".rightpane").css("display", "none");
                $(".leftpane").css("display", "flex");
                $(".pod_product_management").css("display", "none");
                $(".pod_cart_management").removeClass("hide_product_screen_show");
                $(".pod_cart_management").css("display", "flex");
                $(".search-box").css("display", "none");
            }
        }
    }
});
