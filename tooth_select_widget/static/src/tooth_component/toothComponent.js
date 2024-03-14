/** @odoo-module **/

const { Component,onWillUnmount, onMounted, onWillStart,onRendered,mount,onPatched,onWillRender,onWillUpdateProps,whenReady} = owl;
export class ToothComponent extends Component {
	
	clickTooth(toothId){
		this.props.clickTooth(toothId)
	}
}

ToothComponent.template = "tooth_select_widget.ToothComponent";
ToothComponent.components = {};
ToothComponent.defaultProps = {
		clickTooth: () => {},
	};
ToothComponent.props = {
		ToothIds: {
	        type: Object,
	        optional: true,
	    },
	    top:{
	    	type: Boolean,
	        optional: true,
	    },
	    slots: {
	        type: Object,
	        optional: true,
	    },
	    clickTooth: {
	        type: Function,
	        optional: true,
	    },
	};
