import logging


def pre_init_hook(env):
    """Prepopulate stored related fields for faster installation"""
    logger = logging.getLogger(__name__)
    logger.info("Pre-populating stored related fields")
    env.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS company_group_id integer;
        """
    )


def post_init_hook(env):
    """Perform post-installation updates and computations."""

    # Add street3 to address format
    query = """
        UPDATE res_country
        SET address_format = replace(
        address_format,
        E'%(street2)s\n',
        E'%(street2)s\n%(street3)s\n'
        )
    """
    env.cr.execute(query)

    # Map genders to titles
    gender_mappings = {
        "female": env.ref("base.res_partner_title_madam")
        + env.ref("base.res_partner_title_miss"),
        "male": env.ref("base.res_partner_title_mister"),
    }
    for gender, titles in gender_mappings.items():
        env["res.partner"].with_context(active_test=False).search(
            [("title", "in", titles.ids)]
        ).write({"gender": gender})

    # Compute all top parent IDs
    env["res.partner"].compute_all_top_parent_id()


def uninstall_hook(env):
    """Remove street3 from address format"""
    # Remove %(street3)s\n from address_format
    query = """
        UPDATE res_country
        SET address_format = replace(
        address_format,
        E'%(street3)s\n',
        ''
        )
    """
    env.cr.execute(query)

    # Remove %(street3)s from address_format
    query = """
        UPDATE res_country
        SET address_format = replace(
        address_format,
        E'%(street3)s',
        ''
        )
    """
    env.cr.execute(query)


# from odoo import SUPERUSER_ID, api


# def post_init_hook(cr, registry):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     env["res.partner"].compute_all_top_parent_id()
