/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { SetMeasurementPopup } from "@nwpl_pod_master/static/pod_pos_measurements/app/popups/measurement_popup/MeasurementPopup";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(Orderline.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
    },

    async open_set_measurement_popup() {
        console.log("open_set_measurement_popup triggered"); // Debug log

        const orderline = this.props.line.orderline;
        const order = this.pos.get_order();
        
        if (!order) {
            console.error("No active order found");
            return;
        }
        
        const client = order.get_partner();
        if (!client) {
            console.error("No client associated with the order");
            return;
        }

        this.env.services.popup.add(SetMeasurementPopup, {
            partner: client,
            partner_id: client.id,
            info: {
                partner: client,
                sale_order_id: order.name,
            },
            line: orderline,
        });
    },

    // async remove_measurement(measurement_id) {
    //     try {
    //         const orderline = this.props.line.orderline;
    //         if (orderline) {
    //             const index = orderline.measurement_ids.findIndex(m => m.id === measurement_id);
    //             if (index !== -1) {
    //                 orderline.measurement_ids.splice(index, 1);
    //                 console.log("Measurement removed:", measurement_id);
    //                 orderline.order.computeChanges(); 
    //                 this.render(); 
    //             }
    //         }
    //     } catch (error) {
    //         console.error("Error removing measurement:", error);
    //     }
    // },
    
    
    // async remove_measurement(measurement_id) {
    //     try {
    //         const orderline = this.props.line.orderline;
    //         if (orderline) {
    //             const index = orderline.measurement_ids.findIndex(m => m.id === measurement_id);
    //             if (index !== -1) {
    //                 orderline.measurement_ids.splice(index, 1);
    //                 console.log("Measurement removed:", measurement_id);
    //                 this.trigger('update');  
    //                 this.render();   
    //             }
    //         }
    //     } catch (error) {
    //         console.error("Error removing measurement:", error);
    //     }
    // },
    

    async remove_measurement(measurement_id) {
        try {
            const orderline = this.props.line.orderline;
            if (orderline) {
                const index = orderline.measurement_ids.findIndex(m => m.id === measurement_id);
                if (index !== -1) {
                    orderline.measurement_ids.splice(index, 1);
                    orderline.trigger("change", orderline);
                    console.log("Measurement removed:", measurement_id);
                }
            }
        } catch (error) {
            console.error("Error removing measurement:", error);
        }
    },
});

 