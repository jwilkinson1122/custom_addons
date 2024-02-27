/** @odoo-module */

import { sprintf } from "@web/core/utils/strings";
import { parseFloat } from "@web/views/fields/parsers";
import { useBus, useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { ControlButtonsMixin } from "@point_of_sale/app/utils/control_buttons_mixin";
import { Orderline } from "@point_of_sale/app/store/models";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";

import { SaleOrderList } from "@pos_sale/js/OrderManagementScreen/SaleOrderList";
import { SaleOrderManagementControlPanel } from "@pos_sale/js/OrderManagementScreen/SaleOrderManagementControlPanel";
import { Component, onMounted, useRef } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { SalesOrderPopup } from "@pod_create_so_from_pos/js/Popups/SalesOrderPopup";


function getId(fieldVal) {
	return fieldVal && fieldVal[0];
}
const SEARCH_FIELDS = ["name", "partner_id.complete_name", "date_order"];

export class SaleOrderScreen extends ControlButtonsMixin(Component) {
	static storeOnOrder = false;
	static components = { SaleOrderList, SaleOrderManagementControlPanel };
	static template = "pod_create_so_from_pos.SaleOrderScreenWidget";

	setup() {
		super.setup();
		this.pos = usePos();
		this.popup = useService("popup");
		this.orm = useService("orm");
		this.root = useRef("root");
		this.numberBuffer = useService("number_buffer");
		this.saleOrderFetcher = useService("sale_order_fetcher");
		this.notification = useService("pos_notification");
		useBus(this.saleOrderFetcher, "update", this.render);

		onMounted(this.onMounted);
	}
	onMounted() {
		const flexContainer = this.root.el.querySelector(".flex-container");
		const cpEl = this.root.el.querySelector(".control-panel");
		const headerEl = this.root.el.querySelector(".header-row");
		const val = Math.trunc(
			(flexContainer.offsetHeight - cpEl.offsetHeight - headerEl.offsetHeight) /
				headerEl.offsetHeight
		);
		this.saleOrderFetcher.setSearchDomain(this._computeDomain());
		this.saleOrderFetcher.setNPerPage(val);
		this.saleOrderFetcher.fetch();
	}
	_computeDomain() {
        let domain = [
            ["invoice_status", "!=", "invoiced"],
        ];
        const input = this.pos.orderManagement.searchString.trim();
        if (!input) {
            return domain;
        }

        const searchConditions = this.pos.orderManagement.searchString.split(/[,&]\s*/);
        if (searchConditions.length === 1) {
            const cond = searchConditions[0].split(/:\s*/);
            if (cond.length === 1) {
                domain = domain.concat(Array(this.searchFields.length - 1).fill("|"));
                domain = domain.concat(
                    this.searchFields.map((field) => [field, "ilike", `%${cond[0]}%`])
                );
                return domain;
            }
        }

        for (const cond of searchConditions) {
            const [tag, value] = cond.split(/:\s*/);
            if (!this.validSearchTags.has(tag)) {
                continue;
            }
            domain.push([this.fieldMap[tag], "ilike", `%${value}%`]);
        }
        return domain;
    }
    get searchFields() {
        return SEARCH_FIELDS;
    }
	_getSaleOrderOrigin(order) {
		for (const line of order.get_orderlines()) {
			if (line.sale_order_origin_id) {
				return line.sale_order_origin_id;
			}
		}
		return false;
	}
	get selectedPartner() {
		const order = this.pos.orderManagement.selectedOrder;
		return order ? order.get_partner() : null;
	}
	get orders() {
		return this.saleOrderFetcher.get();
	}
	async _setNumpadMode(event) {
		const { mode } = event.detail;
		this.numpadMode = mode;
		this.numberBuffer.reset();
	}
	onNextPage() {
		this.saleOrderFetcher.nextPage();
	}
	onPrevPage() {
		this.saleOrderFetcher.prevPage();
	}
	onSearch(domain) {
		this.saleOrderFetcher.setSearchDomain(domain);
		this.saleOrderFetcher.setPage(1);
		this.saleOrderFetcher.fetch();
	}
	async _onClickSaleOrder(clickedOrder) {
		const { confirmed, payload: selectedOption } = await this.popup.add(SalesOrderPopup, {
			title: this.env._t('Sale Order')  + '  ' + clickedOrder.name,
			list: [
				{
					id: "1",
					label: this.env._t("Confirm Sales Order"),
					item: 'confirm',
					icon: 'fa fa-check-circle',
				},
				{
					id: "2",
					label: this.env._t("Cancel Sales Order"),
					item: 'cancel',
					icon: 'fa fa-close'
				},
			],
		});
		if(confirmed){
			if(selectedOption){
				if(selectedOption === 'confirm'){
					if(clickedOrder.state !== 'sale'){
						var result = await this.orm.call('sale.order', 'action_confirm', [clickedOrder.id]);
						// this.pos.closeScreen();
					}else {
                        await this.popup.add(ConfirmPopup, {
                            title: this.env._t('Already Confirmed'),
                            body: this.env._t(
                                'This Sales Order is Already in confirmed state!!!!'
                            ),
                        });
                    }
				}
				if(selectedOption === 'cancel'){
					if(clickedOrder.state !== 'cancel'){
						var result = await this.orm.call('sale.order', 'action_cancel', [clickedOrder.id]);
						// this.pos.closeScreen();
					}else {
                        await this.popup.add(ConfirmPopup, {
                            title: this.env._t('Already Cancelled'),
                            body: this.env._t(
                                'This Sales Order is Already in Cancel State!!!!'
                            ),
                        });
                    }
				}
			}
		}
	}

	async _getSaleOrder(id) {
		const [sale_order] = await this.orm.read(
			"sale.order",
			[id],
			[
				"order_line",
				"partner_id",
				"pricelist_id",
				"fiscal_position_id",
				"amount_total",
				"amount_untaxed",
				"amount_unpaid",
				"picking_ids",
				"partner_shipping_id",
				"partner_invoice_id",
			]
		);

		const sale_lines = await this._getSOLines(sale_order.order_line);
		sale_order.order_line = sale_lines;

		if (sale_order.picking_ids[0]) {
			const [picking] = await this.orm.read(
				"stock.picking",
				[sale_order.picking_ids[0]],
				["scheduled_date"]
			);
			sale_order.shipping_date = picking.scheduled_date;
		}

		return sale_order;
	}

	async _getSOLines(ids) {
		const so_lines = await this.orm.call("sale.order.line", "read_converted", [ids]);
		return so_lines;
	}
}

registry.category("pos_screens").add("SaleOrderScreen", SaleOrderScreen);