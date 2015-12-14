# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy

from xmodule_django.models import CourseKeyField


class GroupConfiguration(models.Model):
    course_id = CourseKeyField(max_length=255, db_index=True,
            verbose_name=ugettext_lazy(u"Cours"))
    group_id = models.CharField(max_length=100, verbose_name=ugettext_lazy(u"Identifiant du groupe"))
    start_date = models.DateTimeField(verbose_name=ugettext_lazy(u"Debut de la visibilité",))
    end_date = models.DateTimeField(verbose_name=ugettext_lazy(u"Fin de la visibilité",))
    password = models.CharField(max_length=100, verbose_name=ugettext_lazy(u"Mot de passe"))
    duration = models.PositiveIntegerField(verbose_name=ugettext_lazy(u"Durée de disponibilité"))

    class Meta:
        verbose_name = "Groupe de xblocks"
        verbose_name_plural = "Groupes de xblocks"

    def __unicode__(self):
        return "%r - %r" % (self.start_date, self.end_date)


