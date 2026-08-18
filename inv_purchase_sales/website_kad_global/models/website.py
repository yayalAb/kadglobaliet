# -*- coding: utf-8 -*-
from odoo import api, models


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def _kad_sync_menus(self):
        from odoo.addons.website_kad_global.hooks import _sync_website_menus, _unlock_homepage_noupdate
        _unlock_homepage_noupdate(self.env)
        _sync_website_menus(self.env)
        return True
