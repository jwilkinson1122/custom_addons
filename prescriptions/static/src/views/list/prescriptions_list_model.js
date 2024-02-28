/** @odoo-module **/

import { listView } from "@web/views/list/list_view";
import { PrescriptionsModelMixin, PrescriptionsRecordMixin } from "../prescriptions_model_mixin";

const ListModel = listView.Model;
export class PrescriptionsListModel extends PrescriptionsModelMixin(ListModel) {}

PrescriptionsListModel.Record = class PrescriptionsListRecord extends PrescriptionsRecordMixin(ListModel.Record) {};
