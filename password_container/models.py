# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from xmodule_django.models import CourseKeyField


class GroupConfiguration(models.Model):
    course_id = CourseKeyField(max_length=255, db_index=True,
            verbose_name=_(u"Course"))
    group_id = models.CharField(max_length=100, verbose_name=_(u"Group ID"))
    start_date = models.DateTimeField(verbose_name=_(u"Start visibility",))
    end_date = models.DateTimeField(verbose_name=_(u"End Visibility",))
    password = models.CharField(max_length=100, verbose_name=_(u"Password"))
    duration = models.PositiveIntegerField(verbose_name=_(u"Assessment duration"))

    class Meta:
        verbose_name = "Groupe de xblocks"
        verbose_name_plural = "Groupes de xblocks"

    def __unicode__(self):
        return "%r - %r" % (self.start_date, self.end_date)


