# -*- coding: utf-8 -*-
import logging
import requests
from werkzeug import urls
from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    """Class defined for adding Multisafepay payment provider"""
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('multisafepay', "Multisafepay")],
                            ondelete={'multisafepay': 'set default'})
    multisafepay_website_key = fields.Char(string="Website Key",
                                           help="The key solely used to "
                                                "identify the website with "
                                                "multisafepay",
                                           required_if_provider='multisafepay')

    def _multisafepay_make_request(self, endpoint, data=None, method='POST'):
        """Function defined for make request for multisafepay"""
        self.ensure_one()
        endpoint = f'/v1/json/{endpoint.strip("/")}'
        url = urls.url_join('https://testapi.multisafepay.com', endpoint)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": self.multisafepay_website_key,
        }
        try:
            response = requests.request(method, url, json=data, headers=headers,
                                        timeout=60)
        except requests.exceptions.RequestException:
            _logger.exception("unable to communicate with Multisafepay: %s",
                              url)
            raise ValidationError("Multisafepay: " + _(
                "Could not establish the connection to the API."))
        return response.json()
