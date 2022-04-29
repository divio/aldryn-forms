from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class FormsApp(CMSApp):
    name = _('Forms')

    def get_urls(self, *args, **kwargs):
        return ['aldryn_forms.urls']


apphook_pool.register(FormsApp)
