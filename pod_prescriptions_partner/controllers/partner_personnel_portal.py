from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo import http, _
from odoo.exceptions import UserError


class PartnerPersonnelPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        rtn = super()._prepare_home_portal_values(counters)
        partners_domain = self._prepare_partners_domain()
        patients_domain = self._prepare_patients_domain(partners_domain)
        rtn['partners_count'] = http.request.env['prescriptions.partner'].search_count(partners_domain)
        rtn['patients_count'] = http.request.env['prescriptions.patient'].search_count(
            patients_domain)
        return rtn

    @classmethod
    def _prepare_partners_domain(cls):
        user = http.request.env.user
        partner = http.request.env.user.partner_id
        return [
            ('personnel_ids', 'in', partner.partner_personnel_rel_ids.ids),
        ]

    @classmethod
    def _prepare_patients_domain(cls, partners_domain):
        prescriptions_partner_ids = http.request.env['prescriptions.partner'].search(partners_domain).ids
        return [
            ('prescriptions_partner_ids', 'in', prescriptions_partner_ids),
        ]

    @http.route(route=['/my/partners', '/my/partners/page/<int:page>'], type='http', auth='user', website=True)
    def view_partners(self, page=0, **kw):
        """ Display the list of partners that a portal user has access to """
        Partners = http.request.env['prescriptions.partner']
        domain = self._prepare_partners_domain()
        partners_count = Partners.search_count(domain)
        pgr = pager(url='/my/partners', total=partners_count,
                    page=page, step=10, scope=5)
        partners = http.request.env['prescriptions.partner'].search(self._prepare_partners_domain(),
                                                       offset=pgr['offset'],
                                                       limit=partners_count)
        return http.request.render(template='pod_prescriptions_partner.portal_my_partners',
                                   qcontext={
                                       'partners_count': partners_count,
                                       'partners': partners,
                                       'pager': pgr,
                                       'page_name': 'my_partners',
                                   })

    @http.route(route=['/my/partner', '/my/partner/page/<int:page>'], type='http', auth='user', website=True)
    def view_partner(self, prescriptions_partner_id, page=0, **kw):
        """ Display the information for a partner including its list of patients """
        prescriptions_partner_id = int(prescriptions_partner_id)
        prescriptions_partner = http.request.env['prescriptions.partner'].browse(prescriptions_partner_id)
        if not prescriptions_partner:
            raise UserError(_('This partner could not be found.'))
        patients_count = prescriptions_partner.patient_count
        pgr = pager(url=f'/my/partner', total=patients_count, page=page, step=10,
                    scope=5, url_args={'prescriptions_partner_id': prescriptions_partner_id})
        patients = http.request.env['prescriptions.patient'].search([
            ('prescriptions_partner_ids', 'in', prescriptions_partner_id),
        ], offset=pgr['offset'], limit=patients_count)
        return http.request.render(
            template='pod_prescriptions_partner.portal_my_partner_patients',
            qcontext={
                'partner': prescriptions_partner,
                'patients_count': patients_count,
                'patients': patients,
                'pager': pgr,
                'page_name': 'my_partners',
            }
        )

    @http.route(route=['/my/patients', '/my/patients/page/<int:page>'], type='http', auth='user', website=True)
    def view_patients(self, page=0, **kw):
        """ Display the list of patients that the portal user has access to """
        partners_domain = self._prepare_partners_domain()
        patients_domain = self._prepare_patients_domain(partners_domain)
        patients_count = http.request.env['prescriptions.patient'].search_count(patients_domain)
        pgr = pager(url='/my/patients', total=patients_count, page=page, step=10, scope=5)
        patients = http.request.env['prescriptions.patient'].search(patients_domain,
                                                            offset=pgr['offset'],
                                                            limit=patients_count)
        return http.request.render(template='pod_prescriptions_partner.portal_my_patients',
                                   qcontext={
                                       'patients_count': patients_count,
                                       'patients': patients,
                                       'pager': pgr,
                                       'page_name': 'my_patients',
                                   })

    @http.route(route=['/my/patient'], type='http',
                auth='user', website=True)
    def view_patient(self, patient_id, prescriptions_partner_id=None,**kw):
        """ Display the active injuries for a given patient. """
        patient_id = int(patient_id)
        prescriptions_partner_id = prescriptions_partner_id and int(prescriptions_partner_id)
        patient = http.request.env['prescriptions.patient'].browse(patient_id)
        partner = prescriptions_partner_id and http.request.env['prescriptions.partner'].browse(prescriptions_partner_id)
        if not patient:
            raise UserError(_('This patient could not be found.'))
        injuries = patient.injury_ids.filtered(lambda r: r.stage == 'active')
        return http.request.render(
            template='pod_prescriptions_partner.portal_my_patient_injuries',
            qcontext={
                'patient': patient,
                'injuries': injuries,
                'partner': partner,
                'page_name': 'my_patient',
            }
        )
