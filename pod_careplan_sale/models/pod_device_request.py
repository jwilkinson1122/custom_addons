from odoo import models


class PodiatryDeviceRequest(models.Model):
    _inherit = "pod.device.request"

    def check_is_billable(self):
        return self.is_billable

    def compute_price(self, is_insurance):
        cai = (
            self.coverage_agreement_item_id
            or self.request_group_id.coverage_agreement_item_id
        )
        device_price = 0.0
        for admin in self.device_administration_ids:
            device_price += admin.amount
        percentage = cai.coverage_percentage
        if not is_insurance:
            percentage = 100 - percentage
        return (device_price * percentage) / 100

    def check_sellable(self, is_insurance, agreement_item):
        if is_insurance:
            return agreement_item.coverage_percentage > 0
        return agreement_item.coverage_percentage< 100
