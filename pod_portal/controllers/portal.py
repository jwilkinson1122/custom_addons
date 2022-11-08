from odoo.http import route, request
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "patient_prescription_count" in counters:
            count = request.env["pod.prescription"].search_count([])
            values["patient_prescription_count"] = count
        return values

    @route(
        ["/my/patient-prescriptions", "/my/patient-prescriptions/page/<int:page>"],
        auth="user",
        website=True,
    )
    def my_patient_prescriptions(self, page=1, **kw):
        Prescription = request.env["pod.prescription"]
        domain = []
        # Prepare pager data
        prescription_count = Prescription.search_count(domain)
        pager_data = portal.pager(
            url="/my/patient_prescriptions",
            total=prescription_count,
            page=page,
            step=self._items_per_page,
        )
        # Recordset according to pager and domain filter
        prescriptions = Prescription.search(
            domain, limit=self._items_per_page, offset=pager_data["offset"]
        )
        # Prepare template values
        values = self._prepare_portal_layout_values()
        values.update(
            {
                "prescriptions": prescriptions,
                "page_name": "patient-prescriptions",
                "default_url": "/my/patient-prescriptions",
                "pager": pager_data,
            }
        )
        return request.render("pod_portal.my_patient_prescriptions", values)

    @route(["/my/patient-prescription/<model('pod.prescription'):doc>"], auth="user", website=True)
    def portal_my_project(self, doc=None, **kw):
        return request.render("pod_portal.patient_prescription", {"doc": doc})
