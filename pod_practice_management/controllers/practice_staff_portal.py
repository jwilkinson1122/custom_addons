from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo import http, _
from odoo.exceptions import UserError


class PracticeStaffPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        rtn = super()._prepare_home_portal_values(counters)
        practices_domain = self._prepare_practices_domain()
        patients_domain = self._prepare_patients_domain(practices_domain)
        rtn["practices_count"] = http.request.env["podiatry.practice"].search_count(
            practices_domain
        )
        rtn["patients_count"] = http.request.env["podiatry.patient"].search_count(
            patients_domain
        )
        return rtn

    @classmethod
    def _prepare_practices_domain(cls):
        user = http.request.env.user
        return [
            ("staff_ids.user_ids", "in", user.id),
        ]

    @classmethod
    def _prepare_patients_domain(cls, practices_domain):
        practice_ids = (
            http.request.env["podiatry.practice"].search(practices_domain).ids
        )
        return [
            ("practice_ids", "in", practice_ids),
        ]

    @http.route(
        route=["/my/practices", "/my/practices/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def view_practices(self, page=0, **kw):
        """Display the list of practices that a portal user has access to"""
        Practices = http.request.env["podiatry.practice"]
        domain = self._prepare_practices_domain()
        practices_count = Practices.search_count(domain)
        pgr = pager(
            url="/my/practices", total=practices_count, page=page, step=10, scope=5
        )
        practices = http.request.env["podiatry.practice"].search(
            self._prepare_practices_domain(),
            offset=pgr["offset"],
            limit=practices_count,
        )
        return http.request.render(
            template="pod_practice_management.portal_my_practices",
            qcontext={
                "practices_count": practices_count,
                "practices": practices,
                "pager": pgr,
                "page_name": "my_practices",
            },
        )

    @http.route(
        route=["/my/practice", "/my/practice/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def view_practice(self, practice_id, page=0, **kw):
        """Display the information for a practice including its list of patients"""
        practice_id = int(practice_id)
        practice = http.request.env["podiatry.practice"].browse(practice_id)
        if not practice:
            raise UserError(_("This practice could not be found."))
        patients_count = practice.patient_count
        pgr = pager(
            url=f"/my/practice",
            total=patients_count,
            page=page,
            step=10,
            scope=5,
            url_args={"practice_id": practice_id},
        )
        patients = http.request.env["podiatry.patient"].search(
            [
                ("practice_ids", "in", practice_id),
            ],
            offset=pgr["offset"],
            limit=patients_count,
        )
        return http.request.render(
            template="pod_practice_management.portal_my_practice_patients",
            qcontext={
                "practice": practice,
                "patients_count": patients_count,
                "patients": patients,
                "pager": pgr,
                "page_name": "my_practices",
            },
        )

    @http.route(
        route=["/my/patients", "/my/patients/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def view_patients(self, page=0, **kw):
        """Display the list of patients that the portal user has access to"""
        practices_domain = self._prepare_practices_domain()
        patients_domain = self._prepare_patients_domain(practices_domain)
        patients_count = http.request.env["podiatry.patient"].search_count(
            patients_domain
        )
        pgr = pager(
            url="/my/patients", total=patients_count, page=page, step=10, scope=5
        )
        patients = http.request.env["podiatry.patient"].search(
            patients_domain, offset=pgr["offset"], limit=patients_count
        )
        return http.request.render(
            template="pod_practice_management.portal_my_patients",
            qcontext={
                "patients_count": patients_count,
                "patients": patients,
                "pager": pgr,
                "page_name": "my_patients",
            },
        )

    @http.route(route=["/my/patient"], type="http", auth="user", website=True)
    def view_patient(self, patient_id, practice_id=None, **kw):
        """Display the active pathologies for a given patient."""
        patient_id = int(patient_id)
        practice_id = practice_id and int(practice_id)
        patient = http.request.env["podiatry.patient"].browse(patient_id)
        practice = practice_id and http.request.env["podiatry.practice"].browse(
            practice_id
        )
        if not patient:
            raise UserError(_("This patient could not be found."))
        pathologies = patient.pathology_ids.filtered(lambda r: r.status == "active")
        return http.request.render(
            template="pod_practice_management.portal_my_patient_pathologies",
            qcontext={
                "patient": patient,
                "pathologies": pathologies,
                "practice": practice,
                "page_name": "my_patient",
            },
        )
