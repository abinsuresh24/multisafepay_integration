# -*- coding: utf-8 -*-
import logging
import pprint
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MultisafepayController(http.Controller):
    """Class defined for getting return url from the website"""
    _return_url = '/payment/multisafepay/return'
    @http.route(
        _return_url, type='http', auth='public', methods=['GET', 'POST'],
        csrf=False,
        save_session=False
    )
    def multisafepay_return_from_checkout(self, **data):
        """Function defined for getting multisafepay return from checkout"""
        _logger.info("handling redirection from Multisafepay with data:\n%s",
                     pprint.pformat(data))
        request.env['payment.transaction'].sudo()._handle_notification_data(
            'multisafepay', data)
        return request.redirect('/payment/status')
