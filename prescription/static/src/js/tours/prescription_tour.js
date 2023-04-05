odoo.define('prescription.prescription_steps', function (require) {
    "use strict";

    var core = require('web.core');

    var PrescriptionAdditionalTourSteps = core.Class.extend({

        _get_website_prescription_steps: function () {
            return [false];
        },

    });

    return PrescriptionAdditionalTourSteps;

});

odoo.define('prescription.prescription_tour', function (require) {
    "use strict";

    const { _t } = require('web.core');
    const { Markup } = require('web.utils');

    var tour = require('web_tour.tour');
    var PrescriptionAdditionalTourSteps = require('prescription.prescription_steps');

    tour.register('prescription_tour', {
        url: '/web',
        rainbowManMessage: _t("Great! Now all you have to do is wait for your attendees to show up!"),
        sequence: 210,
    }, [tour.stepUtils.showAppsMenuItem(), {
        trigger: '.o_app[data-menu-xmlid="prescription.prescription_main_menu"]',
        content: Markup(_t("Ready to <b>organize prescriptions</b> in a few minutes? Let's get started!")),
        position: 'bottom',
        edition: 'enterprise',
    }, {
        trigger: '.o_app[data-menu-xmlid="prescription.prescription_main_menu"]',
        content: Markup(_t("Ready to <b>organize prescriptions</b> in a few minutes? Let's get started!")),
        edition: 'community',
    }, {
        trigger: '.o-kanban-button-new',
        extra_trigger: '.o_prescription_kanban_view',
        content: Markup(_t("Let's create your first <b>prescription</b>.")),
        position: 'bottom',
        width: 175,
    }, {
        trigger: '.o_prescription_form_view input[name="name"]',
        content: Markup(_t("This is the <b>name</b> your guests will see when registering.")),
        run: 'text Odoo Experience 2020',
    }, {
        trigger: '.o_prescription_form_view input[name="date_end"]',
        content: Markup(_t("When will your prescription take place? <b>Select</b> the start and end dates <b>and click Apply</b>.")),
        run: function () {
            $('input[name="date_begin"]').val('09/30/2020 08:00:00').change();
            $('input[name="date_end"]').val('10/02/2020 23:00:00').change();
        },
    }, {
        trigger: '.o_prescription_form_view div[name="prescription_device_ids"] .o_field_x2many_list_row_add a',
        content: Markup(_t("Device types allow you to distinguish your attendees. Let's <b>create</b> a new one.")),
    }, ...new PrescriptionAdditionalTourSteps()._get_website_prescription_steps(), {
        trigger: '.o_prescription_form_view div[name="stage_id"]',
        extra_trigger: 'div.o_form_buttons_view:not(.o_hidden)',
        content: _t("Now that your prescription is ready, click here to move it to another stage."),
        position: 'bottom',
    }, {
        trigger: 'ol.breadcrumb li.breadcrumb-item:first',
        extra_trigger: '.o_prescription_form_view div[name="stage_id"]',
        content: Markup(_t("Use the <b>breadcrumbs</b> to go back to your kanban overview.")),
        position: 'bottom',
        run: 'click',
    }].filter(Boolean));

});
