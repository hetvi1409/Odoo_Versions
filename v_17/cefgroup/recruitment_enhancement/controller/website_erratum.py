from odoo import http
from odoo.http import request

class CreateProfile(http.Controller):

    @http.route('/eratum', type='http', auth='public', website=True)
    def eratum_display(self, **kw):
        # Fetch only active errata records
        errata = request.env['website.erratum'].sudo().search([('active', '=', True)])
        return request.render('recruitment_enhancement.eratum_template', {
            'errata': errata
        })
