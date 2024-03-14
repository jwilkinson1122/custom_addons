/** @odoo-module */

import { registry } from "@web/core/registry";

export const toothService = {
    dependencies: ["rpc", "orm"],
    async start(env, { rpc, orm }) {
    	const toothIds= await orm.searchRead("tooth.tooth", [], ["id","sequence","name"])
    	console.log("servicetoothIds",toothIds)
    	const treatmentIds= await orm.searchRead("treatment.action", [], ["id","name","checked","action"])
    	function actionTreatement(value) {
            return orm.call(
                'treatment.action',
                'return_treatment_action',
                [false,value]
            );
        }

        return {
    		toothIds,
    		treatmentIds,
    		actionTreatement: actionTreatement,
        };
    },
};

registry.category("services").add("toothService", toothService);
