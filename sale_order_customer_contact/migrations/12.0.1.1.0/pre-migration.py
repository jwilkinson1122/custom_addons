# def migrate(cr, version):
#    # Update field name
#    cr.execute(
#        """
#        ALTER TABLE sale_order
#        RENAME COLUMN customer_contact TO customer_contact_id;
#        """
#    )
#
#    cr.execute(
#        """
#        ALTER TABLE account_invoice
#        RENAME COLUMN customer_contact TO customer_contact_id;
#        """
#    )
