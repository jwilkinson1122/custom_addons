/** @odoo-module **/

import { ButtonCheckBox } from "../button_checkbox/buttonCheckbox";
const { Component} = owl;
//import { toothBus } from "../tooth_bus.js";
export class CustomModal extends Component {
	onModalChangeTraitement(treatmentId, checked){
		this.props.onChangeTraitement(treatmentId, checked)
//		toothBus.trigger("change-traitement",{treatmentId, checked});
	}
	confirm(){
//		toothBus.trigger("modal-confirm");
		
	        this.props.confirm();
	    
	}
}

CustomModal.template = "tooth_select_widget.CustomModal";
CustomModal.components = { ButtonCheckBox };
CustomModal.defaultProps = {
		confirm: () => {},
		onModalChangeTraitement: () => {},
	};
CustomModal.props = {
		treatmentIds: {
	        type: Object,
	        optional: true,
	    },
	    slots: {
	        type: Object,
	        optional: true,
	    },
	    confirm: {
	        type: Function,
	        optional: true,
	    },
	    onChangeTraitement:{
	    	type: Function,
	        optional: true,
	    }
	};