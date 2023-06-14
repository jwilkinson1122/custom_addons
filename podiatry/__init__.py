# See LICENSE file for full copyright and licensing details.

# ----------------------------------------------------------
# A Module for Podiatry Management System
# ----------------------------------------------------------
from odoo import api, SUPERUSER_ID
from . import models
from . import wizard
from . import controllers

from .init_hook import pre_init_hook
from .init_hook import post_init_hook