/** @odoo-module */

import { registry,Registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, useRef, onWillUnmount, onMounted, onWillStart,onRendered,onWillUpdateProps, useState } = owl;
import { ButtonCheckBox } from "../button_checkbox/buttonCheckbox";
import { CustomModal } from "../custom_modal/customModal";
import { ToothComponent } from "../tooth_component/toothComponent";
//import { toothBus } from "../tooth_bus.js";

class ToothSelectField extends Component {
	
	setup() {
	    this.orm = useService("orm");
		const toothService = useService("toothService");
		this.toothService = toothService;
		this.defaultToothIds = toothService.toothIds;
		let toothIds =  [...this.defaultToothIds]
		if (this.props.value){
			if(JSON.parse(this.props.value).length>0)
			toothIds = JSON.parse(this.props.value)
		}
		this.state = useState({ 
			currentTooth: false,
			currenttraitement:[],
			toothIds:toothIds,
			multiSelect:false,
		});
		this.treatmentIds = useState(toothService.treatmentIds);
		this.topToothIds = this.state.toothIds.slice(0,16);
		this.bottomToothIds = this.state.toothIds.slice(-16);
		this.inputRef = useRef("input");

		onWillUpdateProps((nextProps) => {
			var nextValue = [...this.defaultToothIds]
			if (nextProps.value){
				if(JSON.parse(nextProps.value).length>0)
				nextValue = JSON.parse(nextProps.value)
			}
			if (this.props.value !== nextProps.value ) {
				this.state.toothIds = nextValue
				this.topToothIds = this.state.toothIds.slice(0,16);
				this.bottomToothIds = this.state.toothIds.slice(-16);
            }
		});
		
	}
	onMultiSelectChange(ev){
		this.state.multiSelect = !this.state.multiSelect
		if(this.state.multiSelect)
		this.state.currentTooth = []
		else
		this.state.currentTooth = false
	}
	selectAllTooth(){
		this.state.currenttraitement =  []
		this.checkTraitement()
		$('#modaltreatement').modal('toggle');
	}
	selectTooth(toothId) {
		if (this.state.multiSelect){
			this.state.currentTooth.push(toothId);
			var toothIndex = this.state.toothIds.findIndex((tooth)=> tooth.id==toothId)
			var selected = false
			if(this.state.toothIds[toothIndex].muliSelectList)
				selected = true
			this.state.toothIds[toothIndex].muliSelectList = !selected
		}
		else{
			this.state.currentTooth = toothId;
			var toothObj = this.state.toothIds.find((tooth)=> tooth.id==this.state.currentTooth)
			this.state.currenttraitement = toothObj.traitement || []
			this.checkTraitement()
			$('#modaltreatement').modal('toggle');
		}
    	
    }
	onChangeTraitement(resId, checked) {
		var resIdIndex = this.state.currenttraitement.findIndex(t => t === resId)
		if (resIdIndex> -1 && !checked)
		{
			this.state.currenttraitement = this.state.currenttraitement.filter(v => v  != resId);
		}
		if (resIdIndex == -1 && checked){
			this.state.currenttraitement.push(resId)
		}
		this.checkTraitement()
	}
	confirm() {
	    var rec = this
		 this.setTraitement().then(()=>{
		    rec.inputRef.el.value =JSON.stringify(rec.state.toothIds);
            rec.props.update(JSON.stringify(rec.state.toothIds));
            $('#modaltreatement').modal('toggle');
		})

	}
	 async setTraitement(){
		var currenttraitement = []
		var action = false
		var selected = false
		var i=0
		if(this.state.currenttraitement && this.state.currenttraitement.length){
			currenttraitement = this.state.currenttraitement
            action = await this.getAction()
			selected = true
		}
		if(!this.state.multiSelect){
			var currentToothIndex = this.state.toothIds.findIndex((tooth)=> tooth.id == this.state.currentTooth)
			this.state.toothIds[currentToothIndex].traitement = currenttraitement
			this.state.toothIds[currentToothIndex].action = action
			this.state.toothIds[currentToothIndex].selected = selected
		}
		else{
			this.state.toothIds.forEach((value,index) => {
				this.state.currentTooth.forEach((value1,index2)  => {
					if(value.id==value1){
					    i=i+1
						this.state.toothIds[index].traitement = currenttraitement
						this.state.toothIds[index].action =  action
						this.state.toothIds[index].selected = selected
					}
					
				});
				this.state.toothIds[index].muliSelectList = 	false
			});
			this.state.currentTooth = []
		}
	}
    checkTraitement(){
		this.treatmentIds.forEach((value,index) => {
			if(this.state.currenttraitement.indexOf(value.id)!=-1 )
			this.treatmentIds[index]['checked'] = true
			else
			this.treatmentIds[index]['checked'] = false
		});
    }
    async getAction(){
        var actions = false;
        var test ;
        var action_treatement=false
        var nb_tooth_selectionner = this.state.currentTooth.length
        return  await this.toothService.actionTreatement(this.state.currenttraitement)
	}
}
ToothSelectField.template = "tooth_select_widget.ToothSelectField";
ToothSelectField.components = { ButtonCheckBox, CustomModal, ToothComponent };
registry.category("lazy_components").add("ToothSelectField", ToothSelectField);
