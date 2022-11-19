/** @odoo-module */

import { registry } from "@web/core/registry";

function runPoSJSTests({ env }) {
    return {
        type: "item",
        description: env._t("Run Sale JS Tests"),
        callback: () => {
            env.services.action.doAction({
                name: env._t("JS Tests"),
                target: "new",
                type: "ir.actions.act_url",
                url: "/pos/ui/tests?mod=*",
            });
        },
        sequence: 35,
    };
}

registry.category("debug").category("default").add("podiatry_manager.runPoSJSTests", runPoSJSTests);