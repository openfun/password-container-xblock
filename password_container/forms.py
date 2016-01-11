# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy


class PasswordContainerXBlockForm(forms.Form):
    group_id = forms.CharField(label=ugettext_lazy(u"Group ID"),
            help_text=ugettext_lazy(u"All activities with this group ID will be unlocked at the same time."))
    start_date = forms.SplitDateTimeField(label=ugettext_lazy(u"Start visibility"),
            help_text=ugettext_lazy(u"Start date (MM/DD/YYYY) / time (HH/MM/SS, using 24 hour clock) for student to enter the password. Set time in EST the software will show it in UTC"))
    end_date = forms.SplitDateTimeField(label=ugettext_lazy(u"End Visibility"),
            help_text=ugettext_lazy(u"End date (MM/DD/YYYY) / time (HH/MM/SS, using 24 hour clock) for student to enter the password. Set time in EST - the software will show it in UTC"))
    password = forms.CharField(label=ugettext_lazy(u"Password"),
            help_text=ugettext_lazy(u"Password to start the activities"))
    duration = forms.IntegerField(label=ugettext_lazy(u"Assessment duration"),
            help_text=ugettext_lazy(u"Time to complete the ativities once the student has entered the password (in muinutes)"))
