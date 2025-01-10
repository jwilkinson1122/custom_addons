import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    _logger.info("Running pre-migration for version %s", version)

    # Update invalid section_data
    cr.execute(
        """
        UPDATE sale_order_wizard
        SET section_data = '{}'::jsonb
        WHERE section_data IS NULL
           OR section_data::text IN ('false', 'true', '', 'null')
           OR NOT jsonb_typeof(section_data::jsonb) = 'object';
        """
    )
    _logger.info("Pre-migration completed: Invalid section_data fields updated.")
