# -*- coding: utf-8 -*-
import logging
import pprint
import json
import requests
from werkzeug import urls
from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.addons.payment_multisafepay.controllers.main import \
    MultisafepayController

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    """Class defined for Payment transaction using multisafepay"""
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """Function defined for getting specific rendering
        values when confirming payment"""
        url = "https://testapi.multisafepay.com/v1/json/" \
              "orders?api_key=2e84f7c246d3c37f6d12cc3e72b75065fa48be75"
        base_url = self.provider_id.get_base_url()
        redirect_url = urls.url_join(base_url,
                                     MultisafepayController._return_url)
        payload = json.dumps({
            "type": "redirect",
            "order_id": self.reference,
            "gateway": "",
            "currency": self.currency_id.name,
            "amount": int(self.amount),
            "description": "Test order description",
            "payment_options": {
                "notification_url": "https://www.example.com/client/"
                                    "notification?type=notification",
                "notification_method": "POST",
                "redirect_url": f'{redirect_url}?ref={self.reference}',
                "cancel_url": "https://www.example.com/client/"
                              "notification?type=cancel",
                "close_window": True
            },
            "customer": {
                "locale": 'en_US',
                "ip_address": "123.123.123.123",
                "first_name": self.partner_id.name,
                "last_name": self.partner_id.name,
                "company_name": self.company_id.name,
                "address1": self.partner_id.street,
                "house_number": "39C",
                "zip_code": self.partner_id.zip,
                "city": self.partner_id.city,
                "country": self.partner_id.country_id.name,
                "phone": self.partner_id.phone,
                "email": self.partner_id.email,
                "referrer": "https://example.com",
                "user_agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/"
                              "537.36 (KHTML, like Gecko) Chrome/"
                              "38.0.2125.111 Safari/537.36"
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'PHPSESSID=l9b1a2nas4soml8soumke44n6b'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response_json = response.text
        response_data = json.loads(response_json)
        payment_url = response_data["data"]["payment_url"]
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'multisafepay':
            return res
        _logger.info("sending '/orders' request for link creation:\n%s",
                     pprint.pformat(payload))
        payment_data = self.provider_id._multisafepay_make_request('/orders',
                                                                   data=payload)
        self.provider_reference = payment_data.get('id')
        parsed_url = urls.url_parse(payment_url)
        url_params = urls.url_decode(parsed_url.query)
        return {'api_url': payment_url, 'url_params': url_params}

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Function defined for getting notification data
         when confirming payment"""
        transaction = super()._get_tx_from_notification_data(provider_code,
                                                    notification_data)
        if provider_code != 'multisafepay' or len(transaction) == 1:
            return transaction
        transaction = self.search(
            [('reference', '=', notification_data.get('ref')),
             ('provider_code', '=', 'multisafepay')])
        if not transaction:
            raise ValidationError("Multisafepay: " + _(
                "No transaction found matching reference %s.",
                notification_data.get('ref')))
        return transaction

    def _process_notification_data(self, notification_data):
        """Function defined for process notification data
                 when confirming payment"""
        super()._process_notification_data(notification_data)
        if self.provider_code != 'multisafepay':
            return
        order = self.reference
        url = "https://testapi.multisafepay.com/v1/json/orders/" +\
              order + "?api_key=2e84f7c246d3c37f6d12cc3e72b75065fa48be75"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        data = response.json()
        payment_status = data.get('data').get('status')
        if payment_status == 'initialized':
            self._set_pending()
        elif payment_status == 'void':
            self._set_authorized()
        elif payment_status == 'completed':
            self._set_done()
        elif payment_status in ['uncleared', 'canceled', 'declined']:
            self._set_canceled(
                "Multisafepay: " + _("Canceled payment with status: %s",
                                     payment_status))
        else:
            _logger.info(
                "received data with invalid payment status (%s) for transaction"
                "with reference %s", payment_status, self.reference
            )
            self._set_error(
                "Multisafepay: " + _(
                    "Received data with invalid payment status: %s",
                    payment_status)
            )
