/** @odoo-module **/
import { Component, onWillRender } from '@odoo/owl';
import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';
import { usePopover } from '@web/core/popover/popover_hook';
import { standardWidgetProps } from '@web/views/widgets/standard_widget_props';


export class ViewLastSoldPopover extends Component {

    static template = 'custom_sale.ViewLastSoldPopover';
    static props = {
        record: Object
    }

    setup() {
        console.log('Setup Record = ', this.props.record);
        // this.actionService = useService('action');
    }

}

export class ViewLastSoldWidget extends Component {

    static template = 'custom_sale.ViewLastSoldBtn';
    static popOverComponent = ViewLastSoldPopover;
    static props = { ...standardWidgetProps };

    setup() {
        const { data } = this.props.record;
        console.log('data = ', data);
        console.log('last_sold_price = ', data.last_sold_price);
        console.log('data.name = ', data.name);
        console.log('data.name = ', data.currency_id);
        console.log('data.currency = ', data.currency_id.symbol);

        this.popover = usePopover(this.constructor.popOverComponent, { position: "top" })
    }

    showPopover(ev) {
        this.popover.open(ev.currentTarget, { record: this.props.record });
    }
}

export const viewLastSoldWidget = {
    component: ViewLastSoldWidget
}

registry.category('view_widgets').add('view_last_sold_widget', viewLastSoldWidget); 
