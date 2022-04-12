from odoo import http, _
import json
from odoo.http import request
from odoo.addons.restful.controllers.main import validate_token, valid_response, invalid_response
from ..common import json_response, Status


class SubscriptionController(http.Controller):
    @validate_token
    @http.route('/api/subscription/update', methods=["POST"], type='json', auth='none')
    def subscription_update(self, **kwargs):
        params = json.loads(request.httprequest.get_data().decode(request.httprequest.charset))
        code = params.get('code', False)
        app_installed = params.get('apps', False)
        nbr_active_users = params.get('nbr_active_users', False)

        subscription = request.env['sale.subscription'].search([('code', '=', code)])
        if subscription:
            response = {
                'subscription_info': {
                    'expiration_date': subscription.x_studio_end_date,
                    'subscription_code': subscription.code,
                }

            }
            sub_users_count = 0
            allowed_modules = []
            user_product_id = int(request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.user_product_subscription'))
            for line in subscription.recurring_invoice_line_ids:
                if line.product_id.product_tmpl_id.id == user_product_id:
                    sub_users_count += 1
                else:
                    allowed_modules.extend(line.product_id.mapped('tab_module.modules.module_name'))
            if nbr_active_users > sub_users_count:
                response['subscription_info']['expiration_reason'] = _("Exceed number of users !")
                response['subscription_info']['nbr_active_users'] = sub_users_count
            if app_installed != allowed_modules:
                response['subscription_info']['to_uninstall_apps'] = list(set(app_installed) - set(allowed_modules))
                response['subscription_info']['to_install_apps'] = list(set(allowed_modules) - set(app_installed))

            return json_response(data=response)
        return json_response(data={
            'error': _("Subscription Not Found !")
        }, message=Status.FAILED)
