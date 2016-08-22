# -*- coding: utf-8 -*-
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class FormsApp(CMSApp):

    name = _('Forms')
    urls = ['aldryn_forms.urls']

apphook_pool.register(FormsApp)
