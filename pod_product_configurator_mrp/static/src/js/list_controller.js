/** @odoo-module **/
import {ConfigButtonMixin} from "./config_button_mixin.js";
import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";

patch(ListController.prototype, ConfigButtonMixin(".o_list_button_add_config"));
