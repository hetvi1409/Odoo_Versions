from odoo.http import request

from odoo.addons.auth_signup.controllers.main import AuthSignupHome,SIGN_UP_REQUEST_PARAMS
SIGN_UP_REQUEST_PARAMS.add('undertaker')


class AuthSignupHome(AuthSignupHome):

    def _prepare_signup_values(self, qcontext):
        """Adding the undertaken value to the users tab"""
        res = super()._prepare_signup_values(qcontext)
        if qcontext.get('undertaker') == 'on':
            res['undertaker'] = True
        else:
            res['undertaker'] = False
        return res
