# -*- coding: utf-8 -*-


from . import models
from . import controllers
from . import report
from . import wizard
from . import populate


def _synchronize_cron(env):
    send_invoice_cron = env.ref('pod_prescription.send_invoice_cron', raise_if_not_found=False)
    if send_invoice_cron:
        config = env['ir.config_parameter'].get_param('pod_prescription.automatic_invoice', False)
        send_invoice_cron.active = bool(config)
