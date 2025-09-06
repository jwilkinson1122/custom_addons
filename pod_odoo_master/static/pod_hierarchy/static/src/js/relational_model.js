/** @odoo-module **/

import {RelationalModel} from '@web/model/relational_model/relational_model';
import {patch} from '@web/core/utils/patch';
import {getFieldsSpec, getBasicEvalContext, makeActiveField} from "@web/model/relational_model/utils";

patch(RelationalModel.prototype, {

    setup(params, services) {
        super.setup(...arguments);
        this.hooks.onRootLoaded = () => {
            const root = this.root;
            const config = this.root.config;
            if (config.recursive && root.records) {
                this._loadChildren(root.records, config).then(() => {
                    return root;
                });
            }
        }
    },

    // TODO: Modify the domain to include only records with parentField = False in the root search

    async _loadData(config) {
        if (config.recursive) {
            // Dynamically retrieve the parent field
            const parentField = await this._get_parent_field(config.resModel);

            // Ensure only root records are fetched
            const rootDomain = [[parentField, '=', false]];
            if (!config.domain.some(d => d[0] === parentField)) {
                config.domain = config.domain.concat(rootDomain);
            }

            // Include the parent field in active fields if not already present
            if (!(parentField in config.activeFields)) {
                config.activeFields[parentField] = makeActiveField();
            }
        }
        return super._loadData(config);
    },

    async _loadChildren(parentRecords, config) {
        if (!parentRecords || parentRecords.length === 0) return;
    
        const parentField = await this._get_parent_field(config.resModel);
        if (!parentField) return;
    
        // Fetch children for the given parent records
        const parentIds = parentRecords.map((record) => record.resId);
        const childrenData = await this.orm.webSearchRead(
            config.resModel,
            [[parentField, "in", parentIds]],
            {
                context: config.context,
                fields: Object.keys(config.fields),
            }
        );
    
        const childrenByParent = {};
        for (const child of childrenData.records) {
            const parentId = child[parentField]?.id;
            if (!childrenByParent[parentId]) {
                childrenByParent[parentId] = [];
            }
            childrenByParent[parentId].push(child);
        }
    
        // Assign children to parent records
        parentRecords.forEach((record) => {
            if (!record.childrenFetched) {
                record.children = childrenByParent[record.resId] || [];
                record.childrenFetched = true;
            }
        });
    },
    
    async _get_parent_field(model) {
        return await this.orm.call(
            'parent.field.service',
            'get_parent_field',
            [model],
        );
    },

    findRecordInHierarchy(resId) {
        const records = this.root.records;

        function findRecord(records) {
            for (let record of records) {
                if (record.resId === resId) {
                    return record;
                }
                if (record.children && record.children.length > 0) {
                    const found = findRecord(record.children);
                    if (found) {
                        return found;
                    }
                }
            }
        }

        return findRecord(records) || null;
    }
});
