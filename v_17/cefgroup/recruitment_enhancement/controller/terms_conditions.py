from odoo import http
from odoo.http import request

class WebsiteTerms(http.Controller):

    @http.route('/terms-and-conditions', type='http', auth="public", website=True)
    def terms_and_conditions(self, **kw):
        return request.render('recruitment_enhancement.terms_conditions_template')
