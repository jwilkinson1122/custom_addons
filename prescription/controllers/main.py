# -*- coding: utf-8 -*-


from odoo import _, http, fields
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.osv import expression
from odoo.tools import float_round, float_repr


class PrescriptionController(http.Controller):
    @http.route('/prescription/infos', type='json', auth='user')
    def infos(self, user_id=None):
        self._check_user_impersonification(user_id)
        user = request.env['res.users'].browse(user_id) if user_id else request.env.user

        infos = self._make_infos(user, order=False)

        lines = self._get_current_lines(user)
        if lines:
            lines = [{'id': line.id,
                      'product': (line.product_id.id, line.product_id.name, float_repr(float_round(line.price, 2), 2)),
                      'options': [(option.name, float_repr(float_round(option.price, 2), 2))
                                   for option in line.option_ids_1 | line.option_ids_2 | line.option_ids_3],
                      'quantity': line.quantity,
                      'price': line.price,
                      'state': line.state, # Only used for _get_state
                      'note': line.note} for line in lines]
            raw_state, state = self._get_state(lines)
            infos.update({
                'total': float_repr(float_round(sum(line['price'] for line in lines), 2), 2),
                'raw_state': raw_state,
                'state': state,
                'lines': lines,
            })
        return infos

    @http.route('/prescription/trash', type='json', auth='user')
    def trash(self, user_id=None):
        self._check_user_impersonification(user_id)
        user = request.env['res.users'].browse(user_id) if user_id else request.env.user

        lines = self._get_current_lines(user)
        lines.action_cancel()
        lines.unlink()

    @http.route('/prescription/pay', type='json', auth='user')
    def pay(self, user_id=None):
        self._check_user_impersonification(user_id)
        user = request.env['res.users'].browse(user_id) if user_id else request.env.user

        lines = self._get_current_lines(user)
        if lines:
            lines = lines.filtered(lambda line: line.state == 'new')

            lines.action_order()
            return True

        return False

    @http.route('/prescription/payment_message', type='json', auth='user')
    def payment_message(self):
        return {'message': request.env['ir.qweb']._render('prescription.prescription_payment_dialog', {})}

    @http.route('/prescription/user_location_set', type='json', auth='user')
    def set_user_location(self, location_id=None, user_id=None):
        self._check_user_impersonification(user_id)
        user = request.env['res.users'].browse(user_id) if user_id else request.env.user

        user.sudo().last_prescription_location_id = request.env['prescription.location'].browse(location_id)
        return True

    @http.route('/prescription/user_location_get', type='json', auth='user')
    def get_user_location(self, user_id=None):
        self._check_user_impersonification(user_id)
        user = request.env['res.users'].browse(user_id) if user_id else request.env.user

        company_ids = request.env.context.get('allowed_company_ids', request.env.company.ids)
        user_location = user.last_prescription_location_id
        has_multi_company_access = not user_location.company_id or user_location.company_id.id in company_ids

        if not user_location or not has_multi_company_access:
            return request.env['prescription.location'].search([('company_id', 'in', [False] + company_ids)], limit=1).id
        return user_location.id

    def _make_infos(self, user, **kwargs):
        res = dict(kwargs)

        is_manager = request.env.user.has_group('prescription.group_prescription_manager')

        currency = user.company_id.currency_id

        res.update({
            'username': user.sudo().name,
            'userimage': '/web/image?model=res.users&id=%s&field=avatar_128' % user.id,
            'wallet': request.env['prescription.cashmove'].get_wallet_balance(user, False),
            'is_manager': is_manager,
            'group_portal_id': request.env.ref('base.group_portal').id,
            'locations': request.env['prescription.location'].search_read([], ['name']),
            'currency': {'symbol': currency.symbol, 'position': currency.position},
        })

        user_location = user.last_prescription_location_id
        has_multi_company_access = not user_location.company_id or user_location.company_id.id in request._context.get('allowed_company_ids', request.env.company.ids)

        if not user_location or not has_multi_company_access:
            user.last_prescription_location_id = user_location = request.env['prescription.location'].search([], limit=1)

        alert_domain = expression.AND([
            [('available_today', '=', True)],
            [('location_ids', 'in', user_location.id)],
            [('mode', '=', 'alert')],
        ])

        res.update({
            'user_location': (user_location.id, user_location.name),
            'alerts': request.env['prescription.alert'].search_read(alert_domain, ['message']),
        })

        return res

    def _check_user_impersonification(self, user_id=None):
        if (user_id and request.env.uid != user_id and not request.env.user.has_group('prescription.group_prescription_manager')):
            raise AccessError(_('You are trying to impersonate another user, but this can only be done by a prescription manager'))

    def _get_current_lines(self, user):
        return request.env['prescription.order'].search(
            [('user_id', '=', user.id), ('date', '=', fields.Date.context_today(user)), ('state', '!=', 'cancelled')]
            )

    def _get_state(self, lines):
        """
            This method returns the lowest state of the list of lines

            eg: [confirmed, confirmed, new] will return ('new', 'To Order')
        """
        states_to_int = {'new': 0, 'ordered': 1, 'confirmed': 2, 'cancelled': 3}
        int_to_states = ['new', 'ordered', 'confirmed', 'cancelled']
        translated_states = dict(request.env['prescription.order']._fields['state']._description_selection(request.env))

        state = int_to_states[min(states_to_int[line['state']] for line in lines)]

        return (state, translated_states[state])
