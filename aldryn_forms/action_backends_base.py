import abc

import six


class BaseAction(six.with_metaclass(abc.ABCMeta)):

    @abc.abstractproperty
    def verbose_name(self):
        pass  # pragma: no cover

    @abc.abstractmethod
    def form_valid(self, cmsplugin, instance, request, form):
        pass  # pragma: no cover
