# -*- coding: utf-8 -*-

from . import controllers
from . import models


def _prescriptions_project_post_init(env):
    env['project.project'].search([('use_prescriptions', '=', True)])._create_missing_folders()
