# -*- coding: utf-8 -*-
from . import models
from . import controllers
from odoo.addons.payment import setup_provider, reset_payment_provider


def post_init_hook(cr, registry):
    """Set up provider init hook"""
    setup_provider(cr, registry, 'multisafepay')


def uninstall_hook(cr, registry):
    """Reset payment provider uninstall hook"""
    reset_payment_provider(cr, registry, 'multisafepay')
