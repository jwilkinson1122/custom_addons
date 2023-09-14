from odoo.addons.component.core import Component


class AccountMoveMailListener(Component):
    _name = "account.move.storage.listener"
    _inherit = "base.event.listener"
    _apply_on = ["account.move"]

    def _get_exchange_record_vals(self, record):
        return {
            "model": record._name,
            "res_id": record.id,
        }

    def on_post_account_move(self, records):
        for record in records:
            if record.disable_edi_auto:
                continue
            partner = record.partner_id
            if record.move_type not in ["out_invoice", "out_refund"]:
                continue
            if not partner.account_invoice_storage_exchange_type_id:
                continue
            backend = partner.account_invoice_storage_exchange_type_id.backend_id
            if not backend:
                continue
            exchange_type = partner.account_invoice_storage_exchange_type_id.code
            if record._has_exchange_record(exchange_type, backend):
                continue
            exchange_record = backend.create_record(
                exchange_type, self._get_exchange_record_vals(record)
            )
            if record.partner_id.account_invoice_storage_clean_file_name:
                filename = exchange_record.exchange_filename
                exchange_record.exchange_filename = filename.replace("/", "-")
            backend.exchange_generate(exchange_record)
            backend.exchange_send(exchange_record)

    def on_generate_account_edi(self, records):
        return self.on_post_account_move(records)
