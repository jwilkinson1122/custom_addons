odoo.define(
    "pod.tour", function (require) {
        "use strict";
        var core = require('web.core');
        var tour = require('web_tour.tour');
        var _t = core._t;
        tour.STEPS.POD = [
            tour.STEPS.MENU_MORE,
            {
                trigger: '.o_app[data-menu-xmlid="commed.commed_root"], .oe_menu_toggler[data-menu-xmlid="commed.commed_root"]',
                content: _t('Manage electronic medicals records using the <b>NWPL</b> app.'),
                position: 'bottom',
            },
        ];
        tour.register(
            'pod_tour', {
            url: "/web",
        },
            tour.STEPS.POD
        );
    }
);
