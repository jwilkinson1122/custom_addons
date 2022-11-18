odoo.define('podiatry_manager.tour', function (require) {
    "use strict";

    const { _t } = require('web.core');
    const { Markup } = require('web.utils');
    var tour = require('web_tour.tour');

    tour.register('podiatry_manager_tour', {
        url: "/web",
        rainbowMan: false,
        sequence: 45,
    }, [tour.stepUtils.showAppsMenuItem(), {
        trigger: '.o_app[data-menu-xmlid="podiatry_manager.menu_point_root"]',
        content: Markup(_t("Ready to launch your <b>point of sale</b>?")),
        width: 215,
        position: 'right',
        edition: 'community'
    }, {
        trigger: '.o_app[data-menu-xmlid="podiatry_manager.menu_point_root"]',
        content: Markup(_t("Ready to launch your <b>point of sale</b>?")),
        width: 215,
        position: 'bottom',
        edition: 'enterprise'
    }, {
        trigger: ".o_pos_kanban button.oe_kanban_action_button",
        content: Markup(_t("<p>Ready to have a look at the <b>POS Interface</b>? Let's start our first session.</p>")),
        position: "bottom"
    }]);

});
