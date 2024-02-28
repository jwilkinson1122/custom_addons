/** @odoo-module **/

import { addModelNamesToFetch } from '@bus/../tests/helpers/model_definitions_helpers';

addModelNamesToFetch([
    'prescriptions.prescription', 'prescriptions.folder', 'prescriptions.tag', 'prescriptions.share',
    'prescriptions.workflow.rule', 'prescriptions.facet', 'mail.alias',
]);
