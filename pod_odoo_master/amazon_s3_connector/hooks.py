# -*- coding: utf-8 -*-


def uninstall_hook(env):
    """
    Deletes System Parameters
    """
    env["ir.config_parameter"].sudo().search(
        [("key", "=", "pod_odoo_master.amazon_access_key")]
    ).unlink()
    env["ir.config_parameter"].sudo().search(
        [("key", "=", "pod_odoo_master.amazon_secret_key")]
    ).unlink()
    env["ir.config_parameter"].sudo().search(
        [("key", "=", "pod_odoo_master.amazon_bucket_name")]
    ).unlink()
    env["ir.config_parameter"].sudo().search(
        [("key", "=", "pod_odoo_master.amazon_connector")]
    ).unlink()
