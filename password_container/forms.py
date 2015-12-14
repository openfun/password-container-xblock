# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy


class PasswordContainerXBlockForm(forms.Form):
    group_id = forms.CharField(label=ugettext_lazy(u"Identifiant de groupe"),
            help_text=ugettext_lazy(u"Tous les activités ayant cet identifiant en commun seront débloquées en même temps."))
    start_date = forms.SplitDateTimeField(label=ugettext_lazy(u"Debut de la visibilité"),
            help_text=ugettext_lazy(u"Date de début de la visibilité du contenu (UTC)"))
    end_date = forms.SplitDateTimeField(label=ugettext_lazy(u"Fin de la visibilité"),
            help_text=ugettext_lazy(u"Date de fin de la visibilité du contenu (UTC)"))
    password = forms.CharField(label=ugettext_lazy(u"Mot de passe"),
            help_text=ugettext_lazy(u"Mot de passe pour deverouiller le contenu"))
    duration = forms.IntegerField(label=ugettext_lazy(u"Durée de disponibilité"),
            help_text=ugettext_lazy(u"Durée de la disponibilité du contenu en minutes"))
