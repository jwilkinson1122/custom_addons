# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


def post_init_hook(cr, registry):
    cr.execute("""
        UPDATE medical_patient SET species_id = 1
        """)
