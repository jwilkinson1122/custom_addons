/** @odoo-module */

import { PosGlobalState, Order } from "@point_of_sale/js/models";
import { patch } from "@web/core/utils/patch";
import { PosDB } from "@point_of_sale/js/db";
	
	// first one
patch(PosGlobalState.prototype, "wt_abaya.PosGlobalState123", {
	async _processData(loadedData) {
		await this._super(...arguments);
		this.db.measurment_types_by_id = {};
		this.db.measurment_category_by_id = {};
		this.db.measurment_by_id = {};
		this.db.add_measurment_types(loadedData['measurment.type']);
		this.db.add_measurment_categorys(loadedData['measurment.measurment.category']);
		this.db.add_measurments(loadedData['measurment.measurment']);
	},
});
	// second one
// export class AbayaPosGlobalState extends PosGlobalState {
// 	async _processData(loadedData) {
// 		await super._processData(...arguments);
// 		this.db.add_measurment_type(loadedData['measurment.type']);
// 	}
// }
patch(PosDB.prototype, "wt_abaya.PosDB", {
	get_measurment_types_by_id(measurment_type_id){
		if (measurment_type_id instanceof Array) {
			var list = [];
			for (var i = 0, len = measurment_type_id.length; i < len; i++) {
				var measurment_type = this.measurment_types_by_id[measurment_type_id[i]];
				if (measurment_type) {
					list.push(measurment_type);
				} else {
					console.error("get_measurment_types_by_id: no measurment types has id:", measurment_id[i]);
				}
			}
			return list;
		} else {
			return this.measurment_types_by_id[measurment_type_id];
		}
	},
	add_measurment_types(measurment_types){
		if(measurment_types){
			for(var i=0 ; i < measurment_types.length; i++){
				this.measurment_types_by_id[measurment_types[i].id] = measurment_types[i];
			}
		}
	},

	get_measurment_category_by_id(measurment_cat_id){
		if (measurment_cat_id instanceof Array) {
			var list = [];
			for (var i = 0, len = measurment_cat_id.length; i < len; i++) {
				var measurment_cat = this.measurment_category_by_id[measurment_cat_id[i]];
				if (measurment_cat) {
					list.push(measurment_cat);
				} else {
					console.error("get_measurment_category_by_id: no measurment types has id:", measurment_id[i]);
				}
			}
			return list;
		} else {
			return this.measurment_category_by_id[measurment_cat_id];
		}
	},
	add_measurment_categorys(measurment_cats){
		if(measurment_cats){
			for(var i=0 ; i < measurment_cats.length; i++){
				this.measurment_category_by_id[measurment_cats[i].id] = measurment_cats[i];
			}
		}
	},

	get_measurment_by_id(measurment_id){
		if (measurment_id instanceof Array) {
			var list = [];
			for (var i = 0, len = measurment_id.length; i < len; i++) {
				var measurment = this.measurment_by_id[measurment_id[i]];
				if (measurment) {
					list.push(measurment);
				} else {
					console.error("get_measurment_by_id: no measurment types has id:", measurment_id[i]);
				}
			}
			return list;
		} else {
			return this.measurment_by_id[measurment];
		}
	},
	add_measurments(measurments){
		if(measurments){
			for(var i=0 ; i < measurments.length; i++){
				this.measurment_by_id[measurments[i].id] = measurments[i];
			}
		}
	},
});

