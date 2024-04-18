/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosCollection, PosGlobalState, Order, Orderline } from "@point_of_sale/js/models";

patch(Orderline.prototype, "wt_abaya.Orderline", {
	setup(_defaultObj, options) {
        this._super(...arguments);
        this.measurment_ids = this.measurment_ids || {};
        this.measurment_unit = this.measurment_unit || false;
   	},
   	init_from_JSON(json) {
   		this._super(...arguments);
   		this.measurment_ids = json.measurment_ids
   		this.measurment_unit = json.measurment_unit
   		debugger;
   	},
   	// get_measurment_ids(){
   	// 	return this.measurment_ids
   	// },
   	// get_measurment_unit(){
   	// 	return this.measurment_unit;
   	// },
   	set_measurment_ids(measurment_ids){
   		this.measurment_ids = measurment_ids
   	},
   	set_measurment_unit(measurment_unit){
   		this.measurment_unit = measurment_unit
   	},
   	export_as_JSON() {
   		const json = this._super(...arguments);
   		var measurment_list = [];
   		if(this.measurment_ids){
	   		_.each(this.measurment_ids, function(el){
	   			measurment_list.push(el.id);
	   		});
   		}
   		json.measurment_ids = this.measurment_ids || false
   		json.measurment_unit = this.measurment_unit || false
   		if(this.pos.get_order() && this.pos.get_order().finalized){
	   		json.measurment_ids = [[6, 0, measurment_list]]
	   		json.measurment_unit = this.measurment_unit[0] || false
   		}
   		return json
   	}
});