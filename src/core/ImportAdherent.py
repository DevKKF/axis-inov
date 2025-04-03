from django import forms


class ImportAdherent(forms.Form):
    upload_file = forms.FileField()