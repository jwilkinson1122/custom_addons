/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { usePopover } from "@web/core/popover/popover_hook";
import { onPartnerSubRedirect } from './hooks';
import { Component, onWillStart, onWillRender, useState } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

class PartnerOrgChartPopover extends Component {
    static template = "partner_affiliate.partner_org_chart_popover";
    static props = {
        partner: Object,
        close: Function,
    };
    async setup() {
        super.setup();

        this.rpc = useService('rpc');
        this.orm = useService('orm');
        this.actionService = useService("action");
        this._onPartnerSubRedirect = onPartnerSubRedirect();
    }

    async _onPartnerRedirect(partnerId) {
        const action = await this.orm.call('res.partner', 'get_formview_action', [partnerId]);
        this.actionService.doAction(action); 
    }
}

export class PartnerOrgChart extends Component {
    static template = "partner_affiliate.partner_org_chart";
    static props = {...standardFieldProps};
    async setup() {
        super.setup();

        this.rpc = useService('rpc');
        this.orm = useService('orm');
        this.actionService = useService("action");
        this.user = useService("user");
        this.popover = usePopover(PartnerOrgChartPopover);

        this.state = useState({'partner_id': null});
        this.lastParent = null;
        this._onPartnerSubRedirect = onPartnerSubRedirect();

        onWillStart(this.handleComponentUpdate.bind(this));
        onWillRender(this.handleComponentUpdate.bind(this));
    }

    async handleComponentUpdate() {
        this.partner = this.props.record.data;
        this.state.partner_id = this.props.record.resId
        const manager = this.partner.parent_id;
        const forceReload = this.lastRecord !== this.props.record || this.lastParent != manager;
        this.lastParent = manager;
        this.lastRecord = this.props.record;
        await this.fetchPartnerData(this.state.partner_id, forceReload);
    }

    async fetchPartnerData(partnerId, force = false) {
        if (!partnerId) {
            this.managers = [];
            this.affiliates = [];
            this.children = [];
            if (this.view_partner_id) {
                this.render(true);
            }
            this.view_partner_id = null;
        } else if (partnerId !== this.view_partner_id || force) {
            this.view_partner_id = partnerId;
            let orgData = await this.rpc(
                '/partner/get_partner_hierarchy',
                {
                    partner_id: partnerId,
                    context: this.user.context,
                }
            );
            if (Object.keys(orgData).length === 0) {
                orgData = {
                    managers: [],
                    affiliates: [],
                    children: [],
                }
            }
            this.managers = orgData.managers;
            this.affiliates = orgData.affiliates;
            this.children = orgData.children;
            this.managers_more = orgData.managers_more;
            this.self = orgData.self;
            this.render(true);
        }
    }

    _onOpenPopover(event, partner) {
        this.popover.open(event.currentTarget, { partner });
    }

    async _onPartnerRedirect(partnerId) {
        const action = await this.orm.call('res.partner', 'get_formview_action', [partnerId]);
        this.actionService.doAction(action); 
    }

    async _onPartnerMoreManager(managerId) {
        await this.fetchPartnerData(managerId);
        this.state.partner_id = managerId;
    }
}

export const partnerOrgChart = {
    component: PartnerOrgChart,
};

registry.category("fields").add("partner_org_chart", partnerOrgChart );
