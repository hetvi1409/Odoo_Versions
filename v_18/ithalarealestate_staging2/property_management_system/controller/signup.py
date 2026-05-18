from odoo.http import request

from odoo.addons.auth_signup.controllers.main import AuthSignupHome,SIGN_UP_REQUEST_PARAMS
SIGN_UP_REQUEST_PARAMS.add('is_owner')
SIGN_UP_REQUEST_PARAMS.add('is_tenant')
SIGN_UP_REQUEST_PARAMS.add('phone')


class AuthSignupHome(AuthSignupHome):

    def _prepare_signup_values(self, qcontext):
        """Adding the undertaken value to the users tab"""
        res = super()._prepare_signup_values(qcontext)
        if qcontext.get('is_tenant') == 'on':
            res['is_tenant'] = True
        else:
            res['is_tenant'] = False
        if qcontext.get('is_owner') == 'on':
            res['is_owner'] = True
        else:
            res['is_owner'] = False
        if qcontext.get('phone'):
            res['phone'] = qcontext.get('phone')
        return res
