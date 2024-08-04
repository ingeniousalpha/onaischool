from django.utils.translation import gettext_lazy as _

from apps.common.models import AbstractNameModel, PriorityModel


class City(AbstractNameModel, PriorityModel):
    ...

    class Meta:
        verbose_name = _("Город")
        verbose_name_plural = _("Города")
        ordering = ('name__ru', )

