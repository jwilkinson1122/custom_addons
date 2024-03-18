from odoo import models, fields, _

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	pod_product_configure = fields.Boolean(related='pos_config_id.pod_product_configure', readonly=False)
