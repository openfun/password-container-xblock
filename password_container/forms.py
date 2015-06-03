# -*- coding: utf-8 -*-

from django import forms

class PasswordContainerXBlockForm(forms.Form):
    group_id = forms.CharField(label=u"Identifiant de groupe",
            help_text=u"Tous les Xblock ayant cet identifiant en commun seront débloqués en même temps.")
    start_date = forms.SplitDateTimeField(label=u"Debut de la visibilité",
            help_text=u"Children visibility start date and time (UTC)")
    end_date = forms.SplitDateTimeField(label=u"Fin de la visibilité",
            help_text=u"Children visibility end date and time (UTC)")
    password = forms.CharField(label=u"Mot de passe",
            help_text=u"Global password, all student will use this password to unlock content")
    duration = forms.IntegerField(label=u"Durée de disponibilité",
            help_text=u"Durée de la disponibilité du contenu en minutes")
