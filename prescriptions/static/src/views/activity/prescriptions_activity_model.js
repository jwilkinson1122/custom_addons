/** @odoo-module **/

import { ActivityModel } from "@mail/views/web/activity/activity_model";
import { PrescriptionsModelMixin, PrescriptionsRecordMixin } from "../prescriptions_model_mixin";

export class PrescriptionsActivityModel extends PrescriptionsModelMixin(ActivityModel) {}

PrescriptionsActivityModel.Record = class PrescriptionsActivityRecord extends PrescriptionsRecordMixin(ActivityModel.Record) {};

