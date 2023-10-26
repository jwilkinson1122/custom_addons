odoo.define('prescription.test_utils', function (require) {
"use strict";

const AbstractStorageService = require('web.AbstractStorageService');
const RamStorage = require('web.RamStorage');
const {createView} = require('web.test_utils');

/**
 * Helper to create a prescription view with searchpanel
 *
 * @param {object} params
 */
async function createPrescriptionView(params) {
    params.archs = params.archs || {};
    var searchArch = params.archs[`${params.model},false,search`] || '<search></search>';
    var searchPanelArch = `
        <searchpanel>
            <field name="category_id" select="multi" string="Categories" enable_counters="1"/>
            <field name="partner_id" select="multi" string="Partners" enable_counters="1"/>
        </searchpanel>
    `;
    searchArch = searchArch.split('</search>')[0] + searchPanelArch + '</search>';
    params.archs[`${params.model},false,search`] = searchArch;
    if (!params.services || !params.services.local_storage) {
        // the searchPanel uses the localStorage to store/retrieve default
        // active category value
        params.services = params.services || {};
        const RamStorageService = AbstractStorageService.extend({
            storage: new RamStorage(),
        });
        params.services.local_storage = RamStorageService;
    }
    return createView(params);
}

/**
 * Helper to generate a mockRPC function for the mandatory prescription routes (prefixed by '/prescription')
 *
 * @param {object} infos
 * @param {integer} userLocation
 */
function mockPrescriptionRPC({infos, userLocation}) {
    return async function (route) {
        if (route === '/prescription/infos') {
            return Promise.resolve(infos);
        }
        if (route === '/prescription/user_location_get') {
            return Promise.resolve(userLocation);
        }
        return this._super.apply(this, arguments);
    };
}

return {
    createPrescriptionView,
    mockPrescriptionRPC,
};

});
