/** @odoo-module **/
/* eslint-disable sort-imports */

import {_t} from "@web/core/l10n/translation";
import {Dialog} from "@web/core/dialog/dialog";
import {Component, onWillStart, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {WarningDialog} from "@web/core/errors/error_dialogs";
import ProductTmplAttrib from "./product_tmpl_attrib.esm";

export class ConfigureDialog extends Component {
    static components = {Dialog, ProductTmplAttrib};
    static props = {
        productTmplId: Number,
        save: Function,
        close: Function,
        edit: Boolean,
        discard: Function,
    };
    static template = "cpq.ConfigureDialogDialog";

    setup() {
        this.size = "xl";
        this.rpc = useService("rpc");
        this.title = "";  // ✅ Needed for Dialog title
        this.state = useState({
            ptalIds: [],
            selected: {},       // flat for left/right; nested if bilateral
            productTmplId: null,
            valid: false,
            errors: {},
            laterality: "bilateral", // 👣 Added
            split: false,            // 🔄 Added
        });
    
        this.onLateralityChange = (ev) => {
            this.state.laterality = ev.target.value;
            this.state.split = false;
            this.state.selected = {}; // 🔄 reset selection on change
        };
    
        onWillStart(async () => {
            const data = await this._loadData();
            this.title = _t("Configure: %s", data.product_tmpl_id.display_name);  // ✅ Needed
            this.state.ptalIds = data.ptal_ids;
            this.state.productTmplId = data.product_tmpl_id;
        });
    }
    
    async _loadData() {
        return this.rpc(`/cpq/${this.props.productTmplId}/data`, {});
    }

    canCreate() {
        if (!this.state.ptalIds) {
            return false;
        }

        return this.state.valid;
    }

    onCreate() {
        const config = {
            laterality: this.state.laterality,
            split: this.state.split,
            selected: this.state.selected,
        };
    
        return this.rpc(`/cpq/${this.state.productTmplId}/configure`, {
            configuration: config,
        }).then((res) => {
            if (this.props.save) {
                this.props.save(res.product_tmpl_id, res.sale_order_line_id);
            }
            this.onClose();
        });
    }
    

    onClose() {
        // Reset the state
        this.state.ptalIds = [];
        this.state.selected = {};
        this.state.productTmplId = null;
        this.state.valid = false;
        this.state.errors = {};

        if (this.props.discard) {
            this.props.discard();
        }

        this.props.close();
    }

    async _validate() {
        if (this.state.selected) {
            this.rpc(`/cpq/${this.props.productTmplId}/validate`, {
                combination: this.state.selected,
            }).then((res) => {
                this.state.valid = res.valid;
                this.state.errors = res.errors;
            });
        }
    }

    _addOrUpdateSelected(sideOrId, attributeId, valueIdOrPtavId, customValue) {
        const isBilateralSplit = ["left", "right"].includes(sideOrId);
        const side = isBilateralSplit ? sideOrId : null;
        const attrId = isBilateralSplit ? attributeId : sideOrId;
        const ptavId = parseInt(valueIdOrPtavId, 10);
    
        const attr = this.state.ptalIds.find((a) => a.id === attrId);
        if (!attr) return;
    
        if (isBilateralSplit) {
            // Ensure side key exists in state.selected
            if (!this.state.selected[side]) {
                this.state.selected[side] = {};
            }
    
            // Remove any previously selected ptav_id from this attribute
            for (const v of attr.ptav_ids) {
                delete this.state.selected[side][v.id];
            }
    
            const val = attr.ptav_ids.find((v) => v.id === ptavId);
            if (val) {
                this.state.selected[side][ptavId] = val.is_custom && customValue !== undefined
                    ? customValue
                    : val.name;
            }
        } else {
            // Non-split case (Left Only, Right Only, or Bilateral shared)
            const newSelected = {...this.state.selected};
    
            for (const v of attr.ptav_ids) {
                delete newSelected[v.id];
            }
    
            const val = attr.ptav_ids.find((v) => v.id === ptavId);
            if (val) {
                newSelected[ptavId] = val.is_custom && customValue !== undefined
                    ? customValue
                    : val.name;
            }
    
            this.state.selected = newSelected;
        }
    
        this._validate();
    }
    
}

export function ConfigureDialogAction(env, action) {
    if (
        action.context.active_model !== "product.template" ||
        !action.context.active_id
    ) {
        env.services.dialog.add(WarningDialog, {
            body: _t(
                "The product configurator was somehow executed against something which is not a product template. Please contact support."
            ),
            confirm: () => {
                return env.services.action.doAction({
                    type: "ir.actions.act_window_close",
                });
            },
        });
    }
    env.services.dialog.add(ConfigureDialog, {
        productTmplId: action.context.active_id,
        edit: true,
        save: (productTmplId, productId) => {
            return env.services.action.doAction({
                type: "ir.actions.act_window",
                res_model: "product.product",
                views: [[false, "form"]],
                res_id: productId,
            });
        },

        close: () => {
            return env.services.action.doAction({type: "ir.actions.act_window_close"});
        },
        discard: () => {
            return env.services.action.doAction({type: "ir.actions.act_window_close"});
        },
    });
}

registry.category("actions").add("cpq.ConfigureDialogAction", ConfigureDialogAction);
