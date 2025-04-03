from django import forms

from sinistre.models import Sinistre


class SinistreForm(forms.ModelForm):
    class Meta:
        model = Sinistre
        fields = []

    def __init__(self, *args, **kwargs):
        super(SinistreForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
