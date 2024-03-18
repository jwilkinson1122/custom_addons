# -*- coding: utf-8 -*-


from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)


class PosConfigInherit(models.Model):
	_inherit = "pos.config"

	pod_product_configure = fields.Boolean(string="Allow Product Configure",default=True)

