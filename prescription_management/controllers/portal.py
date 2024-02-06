

from odoo.exceptions import AccessError, MissingError
from odoo.http import request, route

from odoo.addons.prescription.controllers import portal


class CustomerPortal(portal.CustomerPortal):

    @route(['/my/prescriptions/<int:prescription_order_id>/update_line_dict'], type='json', auth="public", website=True)
    def portal_quote_option_update(self, prescription_order_id, line_id, access_token=None, remove=False, unlink=False, input_quantity=False, **kwargs):
        """ Update the quantity or Remove an optional RXline from a RX.

        :param int prescription_order_id: `prescription.order` id
        :param int line_id: `prescription.order.line` id
        :param str access_token: portal access_token of the specified order
        :param bool remove: if true, 1 unit will be removed from the line
        :param bool unlink: if true, the option will be removed from the RX
        :param float input_quantity: if specified, will be set as new line qty
        :param dict kwargs: unused parameters
        """
        try:
            prescription_order_sudo = self._document_check_access('prescription.order', prescription_order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # Redundant with can be edited on portal for line, ask prescription if can rbe removed
        if not prescription_order_sudo._can_be_edited_on_portal():
            return False

        prescription_order_line = request.env['prescription.order.line'].sudo().browse(int(line_id)).exists()
        if not prescription_order_line or prescription_order_line.prescription_order_id != prescription_order_sudo:
            return False

        if not prescription_order_line._can_be_edited_on_portal():
            # Do not allow updating non-optional products from a quotation
            return False

        if input_quantity is not False:
            quantity = input_quantity
        else:
            number = -1 if remove else 1
            quantity = prescription_order_line.product_uom_qty + number

        if unlink or quantity <= 0:
            prescription_order_line.unlink()
        else:
            prescription_order_line.product_uom_qty = quantity

    @route(["/my/prescriptions/<int:prescription_order_id>/add_option/<int:option_id>"], type='json', auth="public", website=True)
    def portal_quote_add_option(self, prescription_order_id, option_id, access_token=None, **kwargs):
        """ Add the specified option to the specified order.

        :param int prescription_order_id: `prescription.order` id
        :param int option_id: `prescription.order.option` id
        :param str access_token: portal access_token of the specified order
        :param dict kwargs: unused parameters
        """
        try:
            prescription_order_sudo = self._document_check_access('prescription.order', prescription_order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        option_sudo = request.env['prescription.order.option'].sudo().browse(option_id)

        if prescription_order_sudo != option_sudo.prescription_order_id:
            return request.redirect(prescription_order_sudo.get_portal_url())

        option_sudo.add_option_to_prescription()
