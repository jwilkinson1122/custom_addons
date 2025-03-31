/** @odoo-module **/
/* eslint-disable sort-imports */

import {_t} from "@web/core/l10n/translation";
import {Dialog} from "@web/core/dialog/dialog";
import {Component, onWillStart, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {WarningDialog} from "@web/core/errors/error_dialogs";
import ProductTmplAttrib from "./product_tmpl_attrib.esm";
import SummaryPanel from "./configurator_summary_panel.esm";

// Curent ConfigureDialog

export class ConfigureDialog extends Component {
    static components = {
        Dialog, 
        ProductTmplAttrib,
        SummaryPanel,
    };
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
        this.notification = useService("notification");
        this.state = useState({
            ptalIds: [],
            selected: {},
            productTmplId: null,
            valid: false,
            errors: {},
            laterality: "bilateral",
            split: false,
            undoCache: {
                left: null,
                right: null,
            },
        });

        this.onLateralityChange = (ev) => {
            this.state.laterality = ev.target.value;
            this.state.split = false;
            this.state.selected = {};
        };

        onWillStart(async () => {
            const data = await this._loadData();
            this.title = _t("Configure: %s", data.product_tmpl_id.display_name);
            this.state.ptalIds = data.ptal_ids;
            this.state.productTmplId = data.product_tmpl_id.id;
            // this.state.productTmplId = data.product_tmpl_id;
        });

        this.onSplitToggle = async () => {
            const goingToShared = this.state.split;
            const goingToSplit = !this.state.split;

            const left = this.state.selected.left;
            const right = this.state.selected.right;
            const leftHasData = left && Object.keys(left).length > 0;
            const rightHasData = right && Object.keys(right).length > 0;

            if (goingToShared && (leftHasData || rightHasData)) {
                const confirmed = await this._showConfirmDialog(
                    "Switching to shared mode will erase left and right configurations. Continue?"
                );
                if (!confirmed) return;

                this.state.undoCache.left = JSON.parse(JSON.stringify(this.state.selected.left));
                this.state.undoCache.right = JSON.parse(JSON.stringify(this.state.selected.right));
                this._cleanSide("left");
                this._cleanSide("right");
            }

            if (goingToSplit && leftHasData && !rightHasData) {
                this.state.selected.right = JSON.parse(JSON.stringify(this.state.selected.left));
            }

            if (goingToSplit) {
                this.state.sharedBeforeSplit = JSON.parse(JSON.stringify(this.state.selected));
            }

            this.state.split = !this.state.split;
        };

        this.copyLeftToRight = () => {
            const left = this.state.selected.left;
            if (left && Object.keys(left).length > 0) {
                const validRightPtavIds = new Set(
                    this.state.ptalIds.flatMap((a) => a.ptav_ids.map((v) => v.id))
                );
                const filteredCopy = {};
                for (const [ptavId, value] of Object.entries(left)) {
                    if (validRightPtavIds.has(Number(ptavId))) {
                        filteredCopy[ptavId] = value;
                    }
                }
                if (Object.keys(filteredCopy).length > 0) {
                    this.state.selected.right = JSON.parse(JSON.stringify(filteredCopy));
                    this.notification.add("✅ Copied Left ➡️ Right", { type: "success" });
                } else {
                    this.notification.add("⚠️ No compatible attributes to copy Left ➡️ Right.", { type: "warning" });
                }
            } else {
                this.notification.add("⚠️ Left side has no data to copy.", { type: "warning" });
            }
        };

        this.copyRightToLeft = () => {
            const right = this.state.selected.right;
            if (right && Object.keys(right).length > 0) {
                const validLeftPtavIds = new Set(
                    this.state.ptalIds.flatMap((a) => a.ptav_ids.map((v) => v.id))
                );
                const filteredCopy = {};
                for (const [ptavId, value] of Object.entries(right)) {
                    if (validLeftPtavIds.has(Number(ptavId))) {
                        filteredCopy[ptavId] = value;
                    }
                }
                if (Object.keys(filteredCopy).length > 0) {
                    this.state.selected.left = JSON.parse(JSON.stringify(filteredCopy));
                    this.notification.add("✅ Copied Right ➡️ Left", { type: "success" });
                } else {
                    this.notification.add("⚠️ No compatible attributes to copy Right ➡️ Left.", { type: "warning" });
                }
            } else {
                this.notification.add("⚠️ Right side has no data to copy.", { type: "warning" });
            }
        };
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
        return this.rpc(`/cpq/${this.props.productTmplId}/configure`, {

        // return this.rpc(`/cpq/${this.state.productTmplId}/configure`, {
            configuration: config,
        }).then((res) => {
            if (this.props.save) {
                // Flexible: pass all returned values
                this.props.save(res);
            }
            this.onClose();
        });
    }
    

    onClose() {
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
        if (!this.state.selected) return;
    
        try {
            const res = await this.rpc(`/cpq/${this.props.productTmplId}/validate`, {
                combination: this.state.selected,
            });
            this.state.valid = res.valid;
            this.state.errors = res.errors;
        } catch (error) {
            console.error("🚨 Validation RPC failed:", error);
            this.state.valid = false;
            this.state.errors = { general: "Validation failed due to a server error." };
    
            if (this.notification) {
                this.notification.add("⚠️ Failed to validate configuration. Please try again.", {
                    type: "danger",
                });
            }
        }
    }
    
    _addOrUpdateSelected(sideOrId, attributeId, valueIdOrPtavId, customValue) {
        const isBilateralSplit = ["left", "right"].includes(sideOrId);
        const side = isBilateralSplit ? sideOrId : null;
        const attrId = isBilateralSplit ? attributeId : sideOrId;
        const ptavId = parseInt(valueIdOrPtavId, 10);
    
        const attr = this.state.ptalIds.find((a) => a.id === attrId);
        if (!attr) return;
    
        const val = attr.ptav_ids.find((v) => v.id === ptavId);
        if (!val) return;

        if (isBilateralSplit) {
            const selected = { ...this.state.selected };
            const sideSelected = { ...(selected[side] || {}) };
        
            // Remove all existing ptav.id keys for this attribute
            for (const v of attr.ptav_ids) {
                delete sideSelected[v.id];
            }
        
            const val = attr.ptav_ids.find((v) => v.id === ptavId);
            if (val) {
                sideSelected[ptavId] = val.is_custom && customValue !== undefined ? customValue : val.name;
            }
        
            selected[side] = sideSelected;
            this.state.selected = selected;
        }
    
        // if (isBilateralSplit) {
        //     if (!this.state.selected[side]) {this.state.selected[side] = {};}
    
        //     const sideSelected = { ...this.state.selected[side] };
    
        //     for (const v of attr.ptav_ids) {delete sideSelected[v.id];}
    
        //     sideSelected[ptavId] = val.is_custom && customValue !== undefined ? customValue : val.name;
        //     this.state.selected[side] = sideSelected;
        // } else {
        //     const newSelected = { ...this.state.selected };
    
        //     for (const v of attr.ptav_ids) {
        //         delete newSelected[v.id];
        //     }
    
        //     newSelected[ptavId] = val.is_custom && customValue !== undefined ? customValue : val.name;
        //     this.state.selected = newSelected;
        // }
    
        console.log(`[${side || 'shared'}] updated ${attr.name}:`, this.state.selected);
        this._validate();
    }
    
    _cleanSide(side) {
        if (this.state.selected?.[side]) {
            delete this.state.selected[side];
        }
    }

    _restoreUndoCache() {
        if (this.state.undoCache.left) {
            this.state.selected.left = JSON.parse(JSON.stringify(this.state.undoCache.left));
        }
        if (this.state.undoCache.right) {
            this.state.selected.right = JSON.parse(JSON.stringify(this.state.undoCache.right));
        }
        this._validate();
    }

    async _showConfirmDialog(message) {
        return new Promise((resolve) => {
            this.env.services.dialog.add(WarningDialog, {
                body: message,
                confirmLabel: _t("Yes, continue"),
                cancelLabel: _t("Cancel"),
                confirm: () => resolve(true),
                cancel: () => resolve(false),
            });
        });
    }
}

export function ConfigureDialogAction(env, action) {
    const { context } = action;
    const isFromSaleOrder = context.from_sale_order === true;
    
    if (context.active_model !== "product.template" || !context.active_id) {
        env.services.dialog.add(WarningDialog, {
            body: _t("The product configurator was executed on an invalid model. Contact support."),
            confirm: () => env.services.action.doAction({ type: "ir.actions.act_window_close" }),
        });
        return;
    }

    env.services.dialog.add(ConfigureDialog, {
        productTmplId: context.active_id,
        edit: true,

        save: (res) => {
            if (context.from_sale_order && res.sale_order_line_id) {
                return env.services.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: "sale.order.line",
                    views: [[false, "form"]],
                    res_id: res.sale_order_line_id,
                    target: "current",
                });
            }

            // fallback: just open the product variant
            if (res.product_id) {
                return env.services.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: "product.product",
                    views: [[false, "form"]],
                    res_id: res.product_id,
                    target: "current",
                });
            }

            return env.services.action.doAction({ type: "ir.actions.act_window_close" });
        },

        close: () => env.services.action.doAction({ type: "ir.actions.act_window_close" }),
        discard: () => env.services.action.doAction({ type: "ir.actions.act_window_close" }),
    });
}

registry.category("actions").add("cpq.ConfigureDialogAction", ConfigureDialogAction);

