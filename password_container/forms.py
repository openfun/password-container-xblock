# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _


class PasswordContainerXBlockForm(forms.Form):
    group_id = forms.CharField(label=_(u"Group ID"),
            help_text=_(u"All activities with this group ID will be unlocked at the same time."))
    start_date = forms.SplitDateTimeField(label=_(u"Start visibility"),
            help_text=_(u"Start date (MM/DD/YYYY) / time (HH/MM/SS, using 24 hour clock) for student to enter the password. Set time in EST the software will show it in UTC"))
    end_date = forms.SplitDateTimeField(label=_(u"End Visibility"),
            help_text=_(u"End date (MM/DD/YYYY) / time (HH/MM/SS, using 24 hour clock) for student to enter the password. Set time in EST - the software will show it in UTC"))
    password = forms.CharField(label=_(u"Password"),
            help_text=_(u"Password to start the activities"))
    duration = forms.IntegerField(label=_(u"Assessment duration"),
            help_text=_(u"Time to complete the ativities once the student has entered the password (in muinutes)"))
