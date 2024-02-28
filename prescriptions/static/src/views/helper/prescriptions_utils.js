/** @odoo-module */

export default {
    async get_link_proportion(orm, prescriptions_ids = false, domain = false){
        if (!domain && !prescriptions_ids) {
            return 'none';
        }
        const read_domain = prescriptions_ids.length ? [['id', 'in', prescriptions_ids]] : domain;
        const result = await orm.readGroup(
            'prescriptions.prescription',
            read_domain,
            [],
            ['type']
        );
        if (!result){
            return 'none'
        }
        if (result.every(prescription => prescription['type'] == 'url')){
            return 'all'
        }
        else if (result.some(prescription => prescription['type'] == 'url')) {
            return 'some'
        }
        return 'none'
    },
};
