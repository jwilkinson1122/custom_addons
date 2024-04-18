/** @odoo-module */

import { ConfirmPopup } from "@point_of_sale/js/Popups/ConfirmPopup";
import { AbstractAwaitablePopup } from "@point_of_sale/js/Popups/AbstractAwaitablePopup";
import { _lt } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/pos_hook";
import { renderToElement } from "@web/core/utils/render";
import { useService } from "@web/core/utils/hooks";
import { PosDB } from "@point_of_sale/js/db";
import { ErrorPopup } from "@point_of_sale/js/Popups/ErrorPopup";

export class MeasurmentPopup extends ConfirmPopup {
	static template = "MeasurmentTemplatePopupWidget";
	static defaultProps = { confirmKey: false };
	setup() {
		super.setup();
		this.rpc = useService('rpc');
		this.orm = useService("orm");
		this.db = new PosDB()
		this.pos = usePos();
		Object.assign(this, this.props.info);
	}
	_oncategory(ev){
		var cat_id = parseInt($(ev.currentTarget).val(), 10);
		if (cat_id){
			const category_id = this.pos.globalState.db.get_category_by_id(cat_id)
			if (category_id && category_id.measurment_unit){
				$(".measurment_create_table").find("select[name='Unit_name']").val(category_id.measurment_unit[0])	
			}
			const measurment_type_ids = this.pos.globalState.db.get_measurment_types_by_id(category_id.measurment_type_ids)
			var rendered_measurment_lines = renderToElement('DisplayMeasurmentTypeInput', {'measurment_types': measurment_type_ids});
			$(".measurment_create_table").find(".measurment_create_table_right").html(rendered_measurment_lines);
		}else{
			$(".measurment_create_table").find(".measurment_create_table_right").html('');
		}

	}
	_AddMeasurmentlines(){
		var Measurmentlines = [{'name':'narendra'}]
		var customer_id = parseInt($(".measurments_popup").find("input[name='partner_id']").val())
		var partner_id = this.pos.globalState.db.get_partner_by_id(customer_id)
		if (partner_id){
			var db = this.pos.globalState.db
			var rendered_measurment_lines = renderToElement('DisplayMeasurmentLines', {'partner_id': partner_id, 'db':db});
			$(".hidemeasurmentlinesbtn")[0].style.display = 'block';
			$(".addmeasurmentlinesbtn")[0].style.display = 'none';
			$(".pos_Measurments_table").html(rendered_measurment_lines);
		}
		
	}
	_hideMeasurmentlines(){
		$(".hidemeasurmentlinesbtn")[0].style.display = 'none';
			$(".addmeasurmentlinesbtn")[0].style.display = 'block';
		$(".pos_Measurments_table").html('')
	}
	async confirm() {
		var self = this;
		var error = "";
		var partner_id = $(".measurments_popup").find("input[name='partner_id']").val()
		var measurment = $(".measurment_create_table")
		var date = measurment.find("input[name='measurment_date']").val()
		var category_id = measurment.find("select[name='category_name']").val()
		var unit_id = measurment.find("select[name='Unit_name']").val()
		const measurment_types = measurment.find(".measurment_type_input_cl")
		if (!date){
			error = "Please enter valid date";
		}else if(!category_id){
			error = "Please select categories";
		}else if(!unit_id){
			error = "please select measurment unit";
		}else if(!measurment_types.length){
			error = "please add measurment type..";
		}
		if(!error){
			_.each(measurment_types, function(el){
				if(!$(el).val()){
					error = "Please insert all datas.."
				}
			});
		}
		if(error){
			const body = error
			this.pos.popup.add(ErrorPopup, { title: "Invalid Data", body });
		}else{
			var mtypes = [];
			_.each(measurment_types, function(el){
				mtypes.push({
					// 'measurment_cat_id': parseInt($(".measurment_create_table").find("select[name='category_name']").val()),
					'measurment_type': parseInt($(el).attr('name')),
					'measurment_value': parseInt($(el).val()),
				});
			});
			const desc = {
				'date': date,
				'category_id': parseInt(category_id),
				'measurment_ids': mtypes,
				'partner_id': parseInt(partner_id),
				'measurment_unit': parseInt(unit_id),
			}
			const measurment_category_id = await this.orm.call("res.partner", "add_measurment_category", [
				parseInt(partner_id),
				desc,
			]);
			measurment.find("input[name='measurment_date']").val('')
			measurment.find("select[name='category_name']").val('')
			measurment.find("select[name='Unit_name']").val('')
			measurment.find(".measurment_create_table_right").html('');
			this._AddMeasurmentlines()
		}
	}
}