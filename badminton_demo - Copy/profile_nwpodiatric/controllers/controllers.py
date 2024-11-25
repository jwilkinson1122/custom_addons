# # -*- coding: utf-8 -*-

from odoo.http import request, route, Controller


class WebsitePartnerPage(Controller):

    @route(["/infos-pratiques"], type="http", auth="public", website=True)
    def infos_pratiques(self, **post):
        sport_complex = request.env.ref("profile_nwpodiatric.saintleger_sports_complex")
        return request.render(
            "profile_nwpodiatric.website_practical_information",
            {
                "sport_complex": sport_complex,
                "partner": sport_complex,
            },
        )
