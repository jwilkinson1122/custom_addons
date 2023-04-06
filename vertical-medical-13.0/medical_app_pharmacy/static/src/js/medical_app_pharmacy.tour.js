/* Copyright 2016-2017 LasLabs Inc.
 * License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl) */

odoo.define('medical_app_pharmacy.tour', function (require) {
    'use strict';

    var tour = require('web_tour.tour');
    var _t = require('web.core')._t;

    tour.STEPS.PHARMACY = [
        tour.STEPS.MENU_MORE,
        {
            trigger: '[data-menu-xmlid="medical_app_pharmacy.pharmacy_app_menu"]',
            content: _t('The <b>Pharmacy</b> app allows you to dispense medications in style!'),
            position: 'bottom',
        },
        {
            trigger: '[data-menu-xmlid="medical_app_pharmacy.dispensing_menu"]',
            content: _t('Use the <b>Dispensing</b> section to manage prescription orders.'),
            position: 'bottom',
        },
    ];

    tour.register(
        'medical_app_pharmacy',
        {
            url: '/web',
        },
        tour.STEPS.PHARMACY
    );
});
