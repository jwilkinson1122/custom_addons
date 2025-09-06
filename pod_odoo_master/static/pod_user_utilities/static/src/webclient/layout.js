/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { Sidebar } from "@pod_odoo_master/static/pod_user_utilities/webclient/sidebar/sidebar";
// import { Sidebar } from "@pod_user_utilities/webclient/sidebar/sidebar";

patch(WebClient, {
  components: {
    ...WebClient.components,
    Sidebar,
  },
});
