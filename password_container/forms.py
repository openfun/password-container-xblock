# -*- coding: utf-8 -*-

from django import forms

class PasswordContainerXBlockForm(forms.Form):
    group_id = forms.CharField(label=u"Identifiant de groupe",
            help_text=u"Tous les activités ayant cet identifiant en commun seront débloquées en même temps.")
    start_date = forms.SplitDateTimeField(label=u"Debut de la visibilité",
            help_text=u"Date de début de la visibilité du contenu (UTC)")
    end_date = forms.SplitDateTimeField(label=u"Fin de la visibilité",
            help_text=u"Date de fin de la visibilité du contenu (UTC)")
    password = forms.CharField(label=u"Mot de passe",
            help_text=u"Mot de passe pour deverouiller le contenu")
    duration = forms.IntegerField(label=u"Durée de disponibilité",
            help_text=u"Durée de la disponibilité du contenu en minutes")
