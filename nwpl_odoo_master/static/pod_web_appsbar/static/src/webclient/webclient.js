/** @odoo-module */

import { patch } from "@web/core/utils/patch";

import { WebClient } from "@web/webclient/webclient";
import { AppsBar } from "@nwpl_odoo_master/static/pod_web_appsbar/webclient/appsbar/appsbar";

// import { AppsBar } from "@pod_web_appsbar/webclient/appsbar/appsbar";

patch(WebClient, {
  components: {
    ...WebClient.components,
    AppsBar,
  },
});
