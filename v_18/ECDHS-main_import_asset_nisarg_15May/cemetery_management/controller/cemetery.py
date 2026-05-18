from odoo.http import request, Controller, route
from odoo import http, _


class CemeterySearch(Controller):

    def _get_searchbar_inputs_burial(self):
        return {
            'name': {'input': 'name', 'label': _('Search in Name')},
            'cemetery_id': {'input': 'cemetery_id', 'label': _('Search in Cemetery ID')},
        }

    @route('/cemetery', auth='public', website=True)
    def cemetery_search_view(self, search=None, search_in='name',):
        """function to create the tree view"""
        cemeteries = request.env['cemetery.cemetery'].sudo().search([])
        domain = []
        searchbar_inputs = self._get_searchbar_inputs_burial()
        if search_in == 'name':
            domain += [(search_in, 'ilike', search)]
        if search_in == 'cemetery_id':
            domain += [(search_in, 'ilike', search)]
        cemeteries = request.env['cemetery.cemetery'].sudo().search(domain)
        return request.render(
            'cemetery_management.cemetery_cemetery_search_view',
            {
                'cemeteries': cemeteries,
                'page_name': 'application',
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'search': search,
            })

    @route(['/cemetery-details/<int:cemetery>'],
           type='http', auth='public', website=True)
    def cemetery_details(self, cemetery):
        """Cemetery details"""
        cemetery = request.env['cemetery.cemetery'].sudo().browse(int(cemetery))
        return request.render(
            'cemetery_management.cemetery_cemetery_content_details',
            {
                'cemetery': cemetery,
                'cemetery_id': cemetery.id,
                'show_record': False
            })

    @route('/cemetery-details',
           type='http', auth='public', website=True)
    def cemetery_search_details(self, **kwargs):
        """Cemetery details"""
        cemetery = request.env['cemetery.cemetery'].sudo().browse(int(kwargs['cemetery_id']))
        kwargs['cemetery_id'] = cemetery.id
        kwargs['cemetery'] = cemetery
        kwargs['show_record'] = True
        domain = []
        if kwargs.get('surname'):
            domain += [('surname', 'ilike', kwargs['surname'])]
        if kwargs.get('forenames'):
            domain += [('forenames', 'ilike', kwargs['forenames'])]
        if kwargs.get('date_of_birth'):
            domain += [('date_of_birth', 'ilike', kwargs['date_of_birth'])]
        if kwargs.get('date_of_death'):
            domain += [('date_of_death', 'ilike', kwargs['date_of_death'])]
        death = request.env['death.register'].sudo().search(domain)
        kwargs['death'] = death
        return request.render(
            'cemetery_management.cemetery_cemetery_content_details', kwargs
        )

    @route(['/death-register/<int:death>'],
           type='http', auth='public', website=True)
    def death_register_details(self, death):
        """Cemetery details"""
        death = request.env['death.register'].sudo().browse(death)
        return request.render(
            'cemetery_management.death_register_details',
            {
                'death': death,
            })

    @route(['/death-register'],
           type='http', auth='public', website=True)
    def death_register_search_details(self, **kwargs):
        """Cemetery details"""
        death = request.env['death.register'].sudo().browse(int(kwargs['death']))
        return request.render(
            'cemetery_management.death_register_details',
            {
                'death': death,
            })
